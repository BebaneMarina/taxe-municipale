"""
Routes pour la cartographie et les statistiques géographiques avancées
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, text
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
    db: Session = Depends(get_db)
):
    """
    Récupère les contribuables via la vue cartographie_contribuable_view
    """
    params = {}
    sql = "SELECT * FROM cartographie_contribuable_view"
    if actif is not None:
        sql += " WHERE actif = :actif"
        params["actif"] = actif

    rows = db.execute(text(sql), params).mappings().all()

    result = []
    for row in rows:
        result.append({
            "id": row["id"],
            "nom": row["nom"],
            "prenom": row["prenom"],
            "nom_activite": row["nom_activite"],
            "telephone": row["telephone"],
            "adresse": row["adresse"],
            "latitude": float(row["latitude"]) if row["latitude"] is not None else None,
            "longitude": float(row["longitude"]) if row["longitude"] is not None else None,
            "photo_url": row["photo_url"],
            "type_contribuable": row["type_contribuable"],
            "quartier": row["quartier"],
            "zone": row["zone"],
            "collecteur": row["collecteur"],
            "actif": row["actif"],
            "a_paye": bool(row["a_paye"]),
            "taxes_impayees": row["taxes_impayees"] if row["taxes_impayees"] else [],
            "total_collecte": float(row["total_collecte"]) if row["total_collecte"] is not None else 0.0,
            "nombre_collectes": int(row["nombre_collectes"]) if row["nombre_collectes"] is not None else 0,
            "derniere_collecte": row["derniere_collecte"].isoformat() if row["derniere_collecte"] else None
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

