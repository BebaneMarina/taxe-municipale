"""
Routes pour la cartographie et les statistiques géographiques avancées
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import Optional, List, Dict, Any
from database.database import get_db
from database.models import ZoneGeographique, Quartier, InfoCollecte, StatutCollecteEnum, Contribuable
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel

router = APIRouter(prefix="/api/cartographie", tags=["cartographie"])


class ZoneStatistique(BaseModel):
    """Statistiques pour une zone géographique"""
    nom: str
    total_contribuables: int
    contribuables_payes: int
    contribuables_impayes: int
    taux_paiement: float
    total_collecte: Decimal
    nombre_collectes: int
    collecte_moyenne: Decimal


class StatistiquesCartographie(BaseModel):
    """Statistiques globales pour la cartographie"""
    total_contribuables: int
    contribuables_payes: int
    contribuables_impayes: int
    taux_paiement: float
    total_collecte: Decimal
    collecte_aujourd_hui: Decimal
    collecte_ce_mois: Decimal
    nombre_collecteurs: int
    zones_couvertes: int
    zones_non_couvertes: int
    stats_par_zone: List[ZoneStatistique]


def _to_decimal(value: Any) -> Decimal:
    if isinstance(value, Decimal):
        return value
    if value is None:
        return Decimal('0')
    try:
        return Decimal(str(value))
    except Exception:
        return Decimal('0')


def _fetch_cartography_rows(db: Session) -> List[Dict[str, Any]]:
    rows = db.execute(text("SELECT * FROM cartographie_contribuable_view")).mappings().all()
    return [dict(row) for row in rows]


def _sum_collectes_for_ids(
    db: Session,
    contribuable_ids: List[int],
    date_min: Optional[date] = None,
    date_max: Optional[date] = None,
) -> Decimal:
    if not contribuable_ids:
        return Decimal('0')

    query = db.query(func.sum(InfoCollecte.montant)).filter(
        InfoCollecte.contribuable_id.in_(contribuable_ids),
        InfoCollecte.statut == StatutCollecteEnum.COMPLETED,
        InfoCollecte.annule == False
    )

    if date_min:
        query = query.filter(func.date(InfoCollecte.date_collecte) >= date_min)
    if date_max:
        query = query.filter(func.date(InfoCollecte.date_collecte) <= date_max)

    return query.scalar() or Decimal('0')


def _build_zone_stats(rows: List[Dict[str, Any]]) -> List[ZoneStatistique]:
    zone_map: Dict[str, Dict[str, Any]] = {}
    for row in rows:
        zone_name = row.get("zone") or "Non assigné"
        entry = zone_map.setdefault(zone_name, {
            "nom": zone_name,
            "total_contribuables": 0,
            "contribuables_payes": 0,
            "total_collecte": Decimal('0'),
            "nombre_collectes": 0
        })
        entry["total_contribuables"] += 1
        if row.get("a_paye"):
            entry["contribuables_payes"] += 1
        entry["total_collecte"] += _to_decimal(row.get("total_collecte"))
        entry["nombre_collectes"] += int(row.get("nombre_collectes") or 0)

    zone_stats: List[ZoneStatistique] = []
    for data in zone_map.values():
        total = data["total_contribuables"]
        payes = data["contribuables_payes"]
        impayes = total - payes
        taux = (payes / total * 100) if total > 0 else 0
        collecte_moyenne = (
            data["total_collecte"] / data["nombre_collectes"]
            if data["nombre_collectes"] > 0 else Decimal('0')
        )
        zone_stats.append(ZoneStatistique(
            nom=data["nom"],
            total_contribuables=total,
            contribuables_payes=payes,
            contribuables_impayes=impayes,
            taux_paiement=round(taux, 2),
            total_collecte=data["total_collecte"],
            nombre_collectes=data["nombre_collectes"],
            collecte_moyenne=collecte_moyenne
        ))

    zone_stats.sort(key=lambda z: z.total_collecte, reverse=True)
    return zone_stats


@router.get("/statistiques", response_model=StatistiquesCartographie)
def get_statistiques_cartographie(
    date_debut: Optional[date] = Query(None, description="Date de début pour les statistiques"),
    date_fin: Optional[date] = Query(None, description="Date de fin pour les statistiques"),
    db: Session = Depends(get_db)
):
    """
    Récupère les statistiques complètes pour la cartographie
    """

    rows = _fetch_cartography_rows(db)
    total_contribuables = len(rows)
    contribuables_payes = sum(1 for row in rows if row.get("a_paye"))
    contribuables_impayes = total_contribuables - contribuables_payes
    total_collecte = sum((_to_decimal(row.get("total_collecte"))) for row in rows)
    ids = [row["id"] for row in rows]

    aujourd_hui = date.today()
    debut_mois = date(aujourd_hui.year, aujourd_hui.month, 1)

    collecte_aujourd_hui = _sum_collectes_for_ids(db, ids, aujourd_hui, aujourd_hui)
    collecte_ce_mois = _sum_collectes_for_ids(db, ids, debut_mois, None)

    nombre_collecteurs = len({row.get("collecteur") for row in rows if row.get("collecteur")})
    zones_presentes = {row.get("zone") for row in rows if row.get("zone")}
    zones_couvertes = len(zones_presentes)
    total_zones_actives = db.query(ZoneGeographique).filter(
        ZoneGeographique.actif == True,
        ZoneGeographique.geom.isnot(None)
    ).count()
    zones_non_couvertes = max(total_zones_actives - zones_couvertes, 0)

    stats_par_zone = _build_zone_stats(rows)

    taux_paiement = (contribuables_payes / total_contribuables * 100) if total_contribuables > 0 else 0

    return StatistiquesCartographie(
        total_contribuables=total_contribuables,
        contribuables_payes=contribuables_payes,
        contribuables_impayes=contribuables_impayes,
        taux_paiement=round(taux_paiement, 2),
        total_collecte=total_collecte,
        collecte_aujourd_hui=collecte_aujourd_hui,
        collecte_ce_mois=collecte_ce_mois,
        nombre_collecteurs=nombre_collecteurs,
        zones_couvertes=zones_couvertes,
        zones_non_couvertes=zones_non_couvertes,
        stats_par_zone=stats_par_zone[:10]  # Top 10
    )


@router.get("/evolution-journaliere")
def get_evolution_journaliere(
    jours: int = Query(7, ge=1, le=30, description="Nombre de jours à retourner"),
    db: Session = Depends(get_db)
):
    """
    Récupère l'évolution des collectes sur les N derniers jours
    """
    from datetime import timedelta
    
    date_debut = date.today() - timedelta(days=jours)
    
    collectes = db.query(
        func.date(InfoCollecte.date_collecte).label('jour'),
        func.sum(InfoCollecte.montant).label('montant'),
        func.count(InfoCollecte.id).label('nombre')
    ).filter(
        InfoCollecte.statut == StatutCollecteEnum.COMPLETED,
        InfoCollecte.annule == False,
        func.date(InfoCollecte.date_collecte) >= date_debut
    ).group_by(
        func.date(InfoCollecte.date_collecte)
    ).order_by(
        func.date(InfoCollecte.date_collecte)
    ).all()
    
    # Créer un dictionnaire pour tous les jours
    result = {}
    for i in range(jours):
        jour = date_debut + timedelta(days=i)
        jour_str = jour.strftime('%Y-%m-%d')
        result[jour_str] = {
            'montant': Decimal('0'),
            'nombre': 0
        }
    
    # Remplir avec les données réelles
    for collecte in collectes:
        jour_str = collecte.jour.strftime('%Y-%m-%d')
        if jour_str in result:
            result[jour_str] = {
                'montant': collecte.montant or Decimal('0'),
                'nombre': collecte.nombre or 0
            }
    
    return {
        'jours': [k for k in sorted(result.keys())],
        'montants': [float(result[k]['montant']) for k in sorted(result.keys())],
        'nombres': [result[k]['nombre'] for k in sorted(result.keys())]
    }


@router.get("/map/contribuables")
def get_contribuables_for_map(
    actif: Optional[bool] = Query(True, description="Filtrer par contribuables actifs"),
    db: Session = Depends(get_db)
):
    """
    Retourne les contribuables à afficher sur la carte en se basant
    directement sur la vue `cartographie_contribuable_view`.
    Les coordonnées renvoyées par la vue (réelles ou générées) sont
    utilisées telles quelles pour éviter tout recalcul côté API.
    """
    conditions = []
    params: Dict[str, any] = {}

    if actif is not None:
        conditions.append("actif = :actif")
        params["actif"] = actif

    base_query = "SELECT * FROM cartographie_contribuable_view"
    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)

    rows = db.execute(text(base_query), params).mappings().all()

    result = []
    for row in rows:
        record = dict(row)
        lat = record.get("latitude")
        lon = record.get("longitude")

        if lat is None or lon is None:
            # Impossible d'afficher ce contribuable proprement
            continue

        try:
            latitude = float(lat)
            longitude = float(lon)
        except (TypeError, ValueError):
            continue

        result.append({
            "id": record["id"],
            "nom": record["nom"],
            "prenom": record["prenom"],
            "nom_activite": record["nom_activite"],
            "telephone": record["telephone"],
            "adresse": record["adresse"],
            "latitude": latitude,
            "longitude": longitude,
            "photo_url": record.get("photo_url"),
            "type_contribuable": record.get("type_contribuable"),
            "quartier": record.get("quartier"),
            "zone": record.get("zone"),
            "collecteur": record.get("collecteur"),
            "actif": record.get("actif", True),
            "a_paye": record.get("a_paye", False),
            "taxes_impayees": record.get("taxes_impayees") or [],
            "total_collecte": float(record.get("total_collecte") or 0),
            "nombre_collectes": int(record.get("nombre_collectes") or 0),
            "derniere_collecte": record.get("derniere_collecte"),
            "distance_quartier_m": None
        })

    return result


@router.get("/map/quartiers")
def get_quartiers_for_map(
    actif: Optional[bool] = Query(True, description="Filtrer par quartiers actifs"),
    db: Session = Depends(get_db)
):
    """
    Récupère les quartiers avec leurs géométries pour affichage sur la carte.
    Retourne uniquement les quartiers qui ont une géométrie valide.
    """
    query = (
        db.query(
            Quartier,
            func.ST_AsGeoJSON(Quartier.geom).label("geom_geojson"),
            func.ST_X(Quartier.geom).label("longitude"),
            func.ST_Y(Quartier.geom).label("latitude")
        )
        .filter(
            Quartier.geom.isnot(None),
            Quartier.actif == True if actif else True
        )
    )
    
    if actif is not None:
        query = query.filter(Quartier.actif == actif)
    
    results = query.all()
    
    result = []
    for quartier, geom_geojson, longitude, latitude in results:
        import json
        result.append({
            "id": quartier.id,
            "nom": quartier.nom,
            "code": quartier.code,
            "description": quartier.description,
            "place_type": quartier.place_type,
            "latitude": float(latitude) if latitude is not None else None,
            "longitude": float(longitude) if longitude is not None else None,
            "geom_geojson": json.loads(geom_geojson) if geom_geojson else None,
            "zone": {
                "id": quartier.zone.id,
                "nom": quartier.zone.nom,
                "code": quartier.zone.code
            } if quartier.zone else None,
            "nombre_contribuables": db.query(Contribuable).filter(
                Contribuable.quartier_id == quartier.id,
                Contribuable.actif == True
            ).count()
        })
    
    return result


@router.get("/stats-globales")
def get_stats_globales(db: Session = Depends(get_db)):
    """
    Récupère les statistiques globales pour le dashboard de cartographie
    """
    rows = _fetch_cartography_rows(db)
    total_contribuables = len(rows)
    payes = sum(1 for row in rows if row.get("a_paye"))
    impayes = total_contribuables - payes
    total_collecte = sum((_to_decimal(row.get("total_collecte"))) for row in rows)
    taux_paiement = (payes / total_contribuables * 100) if total_contribuables > 0 else 0
    zones_couvertes = len({row.get("zone") for row in rows if row.get("zone")})
    collecteurs_actifs = len({row.get("collecteur") for row in rows if row.get("collecteur")})

    return {
        "total_contribuables": total_contribuables,
        "contribuables_payes": payes,
        "contribuables_impayes": impayes,
        "taux_paiement": round(taux_paiement, 2),
        "total_collecte": float(total_collecte),
        "zones_couvertes": zones_couvertes,
        "collecteurs_actifs": collecteurs_actifs
    }


@router.get("/stats-zones")
def get_stats_zones(db: Session = Depends(get_db)):
    """
    Récupère les statistiques par zone géographique
    """
    rows = _fetch_cartography_rows(db)
    zone_stats = _build_zone_stats(rows)
    result = [{
        "nom": stat.nom,
        "total_contribuables": stat.total_contribuables,
        "contribuables_payes": stat.contribuables_payes,
        "contribuables_impayes": stat.contribuables_impayes,
        "taux_paiement": stat.taux_paiement,
        "total_collecte": float(stat.total_collecte)
    } for stat in zone_stats]
    
    return result


@router.get("/evolution-collecte")
def get_evolution_collecte(
    jours: int = Query(7, ge=1, le=30, description="Nombre de jours"),
    db: Session = Depends(get_db)
):
    """
    Récupère l'évolution de la collecte sur les N derniers jours
    """
    from datetime import timedelta
    
    date_debut = date.today() - timedelta(days=jours)
    
    collectes = db.query(
        func.date(InfoCollecte.date_collecte).label('jour'),
        func.sum(InfoCollecte.montant).label('montant')
    ).filter(
        InfoCollecte.statut == StatutCollecteEnum.COMPLETED,
        InfoCollecte.annule == False,
        func.date(InfoCollecte.date_collecte) >= date_debut
    ).group_by(
        func.date(InfoCollecte.date_collecte)
    ).order_by(
        func.date(InfoCollecte.date_collecte)
    ).all()
    
    # Créer un dictionnaire pour tous les jours
    result = {}
    for i in range(jours):
        jour = date_debut + timedelta(days=i)
        jour_str = jour.strftime('%Y-%m-%d')
        result[jour_str] = Decimal('0')
    
    # Remplir avec les données réelles
    for collecte in collectes:
        jour_str = collecte.jour.strftime('%Y-%m-%d')
        if jour_str in result:
            result[jour_str] = collecte.montant or Decimal('0')
    
    return {
        'jours': [k for k in sorted(result.keys())],
        'montants': [float(result[k]) for k in sorted(result.keys())]
    }

