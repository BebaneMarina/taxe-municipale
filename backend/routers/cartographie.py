"""
Routes pour la cartographie et les statistiques géographiques avancées
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, text, or_
from typing import Optional, List, Dict
from database.database import get_db
from database.models import Contribuable, ZoneGeographique, Quartier, InfoCollecte, StatutCollecteEnum, Collecteur
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


@router.get("/statistiques", response_model=StatistiquesCartographie)
def get_statistiques_cartographie(
    date_debut: Optional[date] = Query(None, description="Date de début pour les statistiques"),
    date_fin: Optional[date] = Query(None, description="Date de fin pour les statistiques"),
    db: Session = Depends(get_db)
):
    """
    Récupère les statistiques complètes pour la cartographie
    """
    from database.models import AffectationTaxe
    
    # Date de référence
    aujourd_hui = date.today()
    debut_mois = date(aujourd_hui.year, aujourd_hui.month, 1)
    
    # Total contribuables actifs
    total_contribuables = db.query(Contribuable).filter(
        Contribuable.actif == True,
        Contribuable.latitude.isnot(None),
        Contribuable.longitude.isnot(None)
    ).count()
    
    # Contribuables avec paiement à jour
    contribuables_payes = 0
    contribuables_impayes = 0
    
    contribuables = db.query(Contribuable).filter(
        Contribuable.actif == True,
        Contribuable.latitude.isnot(None),
        Contribuable.longitude.isnot(None)
    ).all()
    
    for contrib in contribuables:
        # Vérifier les affectations actives
        affectations = db.query(AffectationTaxe).filter(
            AffectationTaxe.contribuable_id == contrib.id,
            AffectationTaxe.actif == True,
            AffectationTaxe.date_debut <= datetime.utcnow(),
            (
                (AffectationTaxe.date_fin.is_(None)) |
                (AffectationTaxe.date_fin >= datetime.utcnow())
            )
        ).all()
        
        a_paye = True
        if affectations:
            for affectation in affectations:
                date_reference = max(affectation.date_debut.date(), debut_mois)
                collecte = db.query(InfoCollecte).filter(
                    InfoCollecte.contribuable_id == contrib.id,
                    InfoCollecte.taxe_id == affectation.taxe_id,
                    InfoCollecte.statut == StatutCollecteEnum.COMPLETED,
                    InfoCollecte.annule == False,
                    func.date(InfoCollecte.date_collecte) >= date_reference
                ).first()
                
                if not collecte:
                    a_paye = False
                    break
        
        if a_paye:
            contribuables_payes += 1
        else:
            contribuables_impayes += 1
    
    taux_paiement = (contribuables_payes / total_contribuables * 100) if total_contribuables > 0 else 0
    
    # Statistiques de collecte
    query_collectes = db.query(InfoCollecte).filter(
        InfoCollecte.statut == StatutCollecteEnum.COMPLETED,
        InfoCollecte.annule == False
    )
    
    total_collecte = query_collectes.with_entities(
        func.sum(InfoCollecte.montant)
    ).scalar() or Decimal('0')
    
    # Collecte aujourd'hui
    collecte_aujourd_hui = db.query(InfoCollecte).filter(
        InfoCollecte.statut == StatutCollecteEnum.COMPLETED,
        InfoCollecte.annule == False,
        func.date(InfoCollecte.date_collecte) == aujourd_hui
    ).with_entities(func.sum(InfoCollecte.montant)).scalar() or Decimal('0')
    
    # Collecte ce mois
    collecte_ce_mois = db.query(InfoCollecte).filter(
        InfoCollecte.statut == StatutCollecteEnum.COMPLETED,
        InfoCollecte.annule == False,
        func.date(InfoCollecte.date_collecte) >= debut_mois
    ).with_entities(func.sum(InfoCollecte.montant)).scalar() or Decimal('0')
    
    # Nombre de collecteurs actifs
    nombre_collecteurs = db.query(Collecteur).filter(
        Collecteur.actif == True
    ).count()
    
    # Zones couvertes
    zones_couvertes = db.query(ZoneGeographique).filter(
        ZoneGeographique.actif == True,
        ZoneGeographique.geom.isnot(None)
    ).count()
    
    # Statistiques par zone
    stats_par_zone = []
    zones = db.query(ZoneGeographique).filter(
        ZoneGeographique.actif == True
    ).all()
    
    for zone in zones:
        # Contribuables dans cette zone (via quartier)
        quartiers_zone = db.query(Quartier).filter(
            Quartier.zone_id == zone.id,
            Quartier.actif == True
        ).all()
        
        quartier_ids = [q.id for q in quartiers_zone]
        if not quartier_ids:
            continue
        
        contribuables_zone = db.query(Contribuable).filter(
            Contribuable.actif == True,
            Contribuable.quartier_id.in_(quartier_ids),
            Contribuable.latitude.isnot(None),
            Contribuable.longitude.isnot(None)
        ).all()
        
        total_zone = len(contribuables_zone)
        if total_zone == 0:
            continue
        
        payes_zone = 0
        total_collecte_zone = Decimal('0')
        nombre_collectes_zone = 0
        
        for contrib in contribuables_zone:
            # Vérifier le statut de paiement
            affectations = db.query(AffectationTaxe).filter(
                AffectationTaxe.contribuable_id == contrib.id,
                AffectationTaxe.actif == True
            ).all()
            
            a_paye = True
            if affectations:
                for affectation in affectations:
                    date_ref = max(affectation.date_debut.date(), debut_mois)
                    collecte = db.query(InfoCollecte).filter(
                        InfoCollecte.contribuable_id == contrib.id,
                        InfoCollecte.taxe_id == affectation.taxe_id,
                        InfoCollecte.statut == StatutCollecteEnum.COMPLETED,
                        InfoCollecte.annule == False,
                        func.date(InfoCollecte.date_collecte) >= date_ref
                    ).first()
                    
                    if not collecte:
                        a_paye = False
                        break
            
            if a_paye:
                payes_zone += 1
            
            # Collectes du contribuable
            collectes = db.query(InfoCollecte).filter(
                InfoCollecte.contribuable_id == contrib.id,
                InfoCollecte.statut == StatutCollecteEnum.COMPLETED,
                InfoCollecte.annule == False
            ).all()
            
            for collecte in collectes:
                total_collecte_zone += collecte.montant
                nombre_collectes_zone += 1
        
        taux_zone = (payes_zone / total_zone * 100) if total_zone > 0 else 0
        collecte_moyenne_zone = (total_collecte_zone / nombre_collectes_zone) if nombre_collectes_zone > 0 else Decimal('0')
        
        stats_par_zone.append(ZoneStatistique(
            nom=zone.nom,
            total_contribuables=total_zone,
            contribuables_payes=payes_zone,
            contribuables_impayes=total_zone - payes_zone,
            taux_paiement=round(taux_zone, 2),
            total_collecte=total_collecte_zone,
            nombre_collectes=nombre_collectes_zone,
            collecte_moyenne=collecte_moyenne_zone
        ))
    
    # Trier par total_collecte décroissant
    stats_par_zone.sort(key=lambda x: x.total_collecte, reverse=True)
    
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
        zones_non_couvertes=0,  # À calculer si nécessaire
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
    distance_max_m: Optional[float] = Query(
        None,
        description="Distance maximale en mètres par rapport au quartier (laisser vide pour tout afficher)",
    ),
    fallback_distance_m: float = Query(
        1000.0,
        description="Si un contribuable est plus éloigné que cette distance de son quartier, on affiche le point du quartier",
    ),
    db: Session = Depends(get_db)
):
    """
    Récupère les contribuables avec coordonnées GPS valides et assignés à un quartier.
    Filtre les points qui sont trop loin des quartiers (pour éviter l'affichage sur l'eau).
    """
    from database.models import Contribuable, Quartier
    
    # Construire la requête avec jointure spatiale
    # On calcule toujours la distance au quartier ; on ne filtre que si distance_max_m est fourni
    distance_expr = func.ST_DistanceSphere(Contribuable.geom, Quartier.geom)

    query = (
        db.query(
            Contribuable,
            Quartier,
            distance_expr.label("distance_m"),
            func.ST_X(Quartier.geom).label("quartier_lon"),
            func.ST_Y(Quartier.geom).label("quartier_lat"),
        )
        .join(Quartier, Contribuable.quartier_id == Quartier.id)
        .filter(
            Quartier.geom.isnot(None),
            Quartier.actif == True,
        )
    )
    
    if actif is not None:
        query = query.filter(Contribuable.actif == actif)
    if distance_max_m is not None:
        query = query.filter(
            or_(
                Contribuable.geom.is_(None),
                distance_expr <= distance_max_m
            )
        )
    
    results = query.all()
    
    # Récupérer les statistiques de collecte pour chaque contribuable
    from database.models import InfoCollecte, AffectationTaxe, StatutCollecteEnum
    
    aujourd_hui = date.today()
    debut_mois = date(aujourd_hui.year, aujourd_hui.month, 1)
    
    result = []
    for contrib, quartier, distance_m, quartier_lon, quartier_lat in results:
        # Vérifier le statut de paiement
        affectations = db.query(AffectationTaxe).filter(
            AffectationTaxe.contribuable_id == contrib.id,
            AffectationTaxe.actif == True,
            AffectationTaxe.date_debut <= datetime.utcnow(),
            (
                (AffectationTaxe.date_fin.is_(None)) |
                (AffectationTaxe.date_fin >= datetime.utcnow())
            )
        ).all()
        
        a_paye = True
        taxes_impayees = []
        if affectations:
            for affectation in affectations:
                date_ref = max(affectation.date_debut.date(), debut_mois)
                collecte = db.query(InfoCollecte).filter(
                    InfoCollecte.contribuable_id == contrib.id,
                    InfoCollecte.taxe_id == affectation.taxe_id,
                    InfoCollecte.statut == StatutCollecteEnum.COMPLETED,
                    InfoCollecte.annule == False,
                    func.date(InfoCollecte.date_collecte) >= date_ref
                ).first()
                
                if not collecte:
                    a_paye = False
                    from database.models import Taxe
                    taxe = db.query(Taxe).filter(Taxe.id == affectation.taxe_id).first()
                    if taxe:
                        taxes_impayees.append(taxe.nom)
        
        # Statistiques de collecte
        collectes = db.query(InfoCollecte).filter(
            InfoCollecte.contribuable_id == contrib.id,
            InfoCollecte.statut == StatutCollecteEnum.COMPLETED,
            InfoCollecte.annule == False
        ).all()
        
        total_collecte = sum(c.montant for c in collectes) or Decimal('0')
        nombre_collectes = len(collectes)
        derniere_collecte = max([c.date_collecte for c in collectes], default=None)
        
        # Choisir le point à afficher : si trop éloigné, utiliser le point du quartier
        use_quartier_point = (
            distance_m is None or
            (fallback_distance_m is not None and distance_m > fallback_distance_m)
        )
        latitude = (
            float(quartier_lat) if use_quartier_point and quartier_lat is not None
            else (float(contrib.latitude) if contrib.latitude is not None else None)
        )
        longitude = (
            float(quartier_lon) if use_quartier_point and quartier_lon is not None
            else (float(contrib.longitude) if contrib.longitude is not None else None)
        )

        result.append({
            "id": contrib.id,
            "nom": contrib.nom,
            "prenom": contrib.prenom,
            "nom_activite": contrib.nom_activite,
            "telephone": contrib.telephone,
            "adresse": contrib.adresse,
            "latitude": latitude,
            "longitude": longitude,
            "photo_url": contrib.photo_url,
            "type_contribuable": contrib.type_contribuable.nom if contrib.type_contribuable else None,
            "quartier": quartier.nom if quartier else None,
            "zone": quartier.zone.nom if quartier and quartier.zone else None,
            "collecteur": f"{contrib.collecteur.nom} {contrib.collecteur.prenom or ''}".strip() if contrib.collecteur else None,
            "actif": contrib.actif,
            "a_paye": a_paye,
            "taxes_impayees": taxes_impayees,
            "total_collecte": float(total_collecte),
            "nombre_collectes": nombre_collectes,
            "derniere_collecte": derniere_collecte.isoformat() if derniere_collecte else None,
            "distance_quartier_m": float(distance_m) if distance_m is not None else None
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
    from database.models import AffectationTaxe
    
    aujourd_hui = date.today()
    debut_mois = date(aujourd_hui.year, aujourd_hui.month, 1)
    
    # Total contribuables actifs avec coordonnées GPS
    total_contribuables = db.query(Contribuable).filter(
        Contribuable.actif == True,
        Contribuable.latitude.isnot(None),
        Contribuable.longitude.isnot(None)
    ).count()
    
    # Contribuables payés et impayés
    contribuables = db.query(Contribuable).filter(
        Contribuable.actif == True,
        Contribuable.latitude.isnot(None),
        Contribuable.longitude.isnot(None)
    ).all()
    
    payes = 0
    impayes = 0
    
    for contrib in contribuables:
        affectations = db.query(AffectationTaxe).filter(
            AffectationTaxe.contribuable_id == contrib.id,
            AffectationTaxe.actif == True,
            AffectationTaxe.date_debut <= datetime.utcnow(),
            (
                (AffectationTaxe.date_fin.is_(None)) |
                (AffectationTaxe.date_fin >= datetime.utcnow())
            )
        ).all()
        
        a_paye = True
        if affectations:
            for affectation in affectations:
                date_ref = max(affectation.date_debut.date(), debut_mois)
                collecte = db.query(InfoCollecte).filter(
                    InfoCollecte.contribuable_id == contrib.id,
                    InfoCollecte.taxe_id == affectation.taxe_id,
                    InfoCollecte.statut == StatutCollecteEnum.COMPLETED,
                    InfoCollecte.annule == False,
                    func.date(InfoCollecte.date_collecte) >= date_ref
                ).first()
                
                if not collecte:
                    a_paye = False
                    break
        
        if a_paye:
            payes += 1
        else:
            impayes += 1
    
    taux_paiement = (payes / total_contribuables * 100) if total_contribuables > 0 else 0
    
    # Total collecte
    total_collecte = db.query(InfoCollecte).filter(
        InfoCollecte.statut == StatutCollecteEnum.COMPLETED,
        InfoCollecte.annule == False
    ).with_entities(func.sum(InfoCollecte.montant)).scalar() or Decimal('0')
    
    # Zones couvertes
    zones_couvertes = db.query(ZoneGeographique).filter(
        ZoneGeographique.actif == True
    ).count()
    
    # Collecteurs actifs
    collecteurs_actifs = db.query(Collecteur).filter(
        Collecteur.actif == True
    ).count()
    
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
    from database.models import AffectationTaxe
    
    aujourd_hui = date.today()
    debut_mois = date(aujourd_hui.year, aujourd_hui.month, 1)
    
    zones = db.query(ZoneGeographique).filter(
        ZoneGeographique.actif == True
    ).all()
    
    result = []
    for zone in zones:
        quartiers_zone = db.query(Quartier).filter(
            Quartier.zone_id == zone.id,
            Quartier.actif == True
        ).all()
        
        quartier_ids = [q.id for q in quartiers_zone]
        if not quartier_ids:
            continue
        
        contribuables_zone = db.query(Contribuable).filter(
            Contribuable.actif == True,
            Contribuable.quartier_id.in_(quartier_ids),
            Contribuable.latitude.isnot(None),
            Contribuable.longitude.isnot(None)
        ).all()
        
        total = len(contribuables_zone)
        if total == 0:
            continue
        
        payes = 0
        total_collecte_zone = Decimal('0')
        
        for contrib in contribuables_zone:
            affectations = db.query(AffectationTaxe).filter(
                AffectationTaxe.contribuable_id == contrib.id,
                AffectationTaxe.actif == True
            ).all()
            
            a_paye = True
            if affectations:
                for affectation in affectations:
                    date_ref = max(affectation.date_debut.date(), debut_mois)
                    collecte = db.query(InfoCollecte).filter(
                        InfoCollecte.contribuable_id == contrib.id,
                        InfoCollecte.taxe_id == affectation.taxe_id,
                        InfoCollecte.statut == StatutCollecteEnum.COMPLETED,
                        InfoCollecte.annule == False,
                        func.date(InfoCollecte.date_collecte) >= date_ref
                    ).first()
                    
                    if not collecte:
                        a_paye = False
                        break
            
            if a_paye:
                payes += 1
            
            # Collectes du contribuable
            collectes = db.query(InfoCollecte).filter(
                InfoCollecte.contribuable_id == contrib.id,
                InfoCollecte.statut == StatutCollecteEnum.COMPLETED,
                InfoCollecte.annule == False
            ).all()
            
            for collecte in collectes:
                total_collecte_zone += collecte.montant
        
        taux = (payes / total * 100) if total > 0 else 0
        
        result.append({
            "nom": zone.nom,
            "total_contribuables": total,
            "contribuables_payes": payes,
            "contribuables_impayes": total - payes,
            "taux_paiement": round(taux, 2),
            "total_collecte": float(total_collecte_zone)
        })
    
    # Trier par total_collecte décroissant
    result.sort(key=lambda x: x['total_collecte'], reverse=True)
    
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

