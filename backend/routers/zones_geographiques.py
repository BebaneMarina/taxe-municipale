"""
Routes pour la gestion des zones géographiques (polygones GeoJSON)
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from database.database import get_db
from database.models import ZoneGeographique
from schemas.zone_geographique import (
    ZoneGeographiqueCreate, 
    ZoneGeographiqueUpdate, 
    ZoneGeographiqueResponse,
    PointLocationRequest,
    PointLocationResponse
)
import json


router = APIRouter(prefix="/api/zones-geographiques", tags=["zones-geographiques"])


def build_geom_from_geojson(geometry: Optional[dict]):
    if not geometry:
        return None
    return func.ST_SetSRID(func.ST_GeomFromGeoJSON(json.dumps(geometry)), 4326)


@router.get("/", response_model=List[ZoneGeographiqueResponse])
def get_zones_geographiques(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    type_zone: Optional[str] = Query(None, description="Filtrer par type (quartier, arrondissement, secteur)"),
    actif: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Récupère la liste des zones géographiques"""
    query = db.query(ZoneGeographique)
    
    if type_zone:
        query = query.filter(ZoneGeographique.type_zone == type_zone)
    if actif is not None:
        query = query.filter(ZoneGeographique.actif == actif)
    
    zones = query.offset(skip).limit(limit).all()
    return zones


@router.get("/{zone_id}", response_model=ZoneGeographiqueResponse)
def get_zone_geographique(zone_id: int, db: Session = Depends(get_db)):
    """Récupère une zone géographique par ID"""
    zone = db.query(ZoneGeographique).filter(ZoneGeographique.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone géographique non trouvée")
    return zone


@router.post("/", response_model=ZoneGeographiqueResponse)
def create_zone_geographique(zone: ZoneGeographiqueCreate, db: Session = Depends(get_db)):
    """Crée une nouvelle zone géographique"""
    data = zone.model_dump()
    db_zone = ZoneGeographique(**data)
    db_zone.geom = build_geom_from_geojson(zone.geometry)
    db.add(db_zone)
    db.commit()
    db.refresh(db_zone)
    return db_zone


@router.put("/{zone_id}", response_model=ZoneGeographiqueResponse)
def update_zone_geographique(
    zone_id: int, 
    zone_update: ZoneGeographiqueUpdate, 
    db: Session = Depends(get_db)
):
    """Met à jour une zone géographique"""
    db_zone = db.query(ZoneGeographique).filter(ZoneGeographique.id == zone_id).first()
    if not db_zone:
        raise HTTPException(status_code=404, detail="Zone géographique non trouvée")
    
    update_data = zone_update.model_dump(exclude_unset=True)
    geometry_value = update_data.pop("geometry", None)
    for field, value in update_data.items():
        setattr(db_zone, field, value)

    if geometry_value is not None:
        db_zone.geometry = geometry_value
        db_zone.geom = build_geom_from_geojson(geometry_value)
    
    db.commit()
    db.refresh(db_zone)
    return db_zone


@router.delete("/{zone_id}")
def delete_zone_geographique(zone_id: int, db: Session = Depends(get_db)):
    """Supprime une zone géographique"""
    db_zone = db.query(ZoneGeographique).filter(ZoneGeographique.id == zone_id).first()
    if not db_zone:
        raise HTTPException(status_code=404, detail="Zone géographique non trouvée")
    
    db.delete(db_zone)
    db.commit()
    return {"message": "Zone géographique supprimée avec succès"}


@router.post("/locate-point", response_model=PointLocationResponse)
def locate_point(request: PointLocationRequest, db: Session = Depends(get_db)):
    """
    Détermine dans quelle zone géographique se trouve un point GPS
    Utilise PostGIS ST_Contains
    """
    point = func.ST_SetSRID(
        func.ST_MakePoint(request.longitude, request.latitude),
        4326
    )

    query = db.query(ZoneGeographique).filter(
        ZoneGeographique.actif == True,
        ZoneGeographique.geom.isnot(None),
        func.ST_Contains(ZoneGeographique.geom, point)
    )

    if request.type_zone:
        query = query.filter(ZoneGeographique.type_zone == request.type_zone)

    zone = query.first()
    if zone:
        return PointLocationResponse(
            zone=zone,
            found=True,
            message=f"Point trouvé dans la zone: {zone.nom}"
        )

    return PointLocationResponse(
        zone=None,
        found=False,
        message="Aucune zone trouvée pour ce point"
    )


@router.get("/map/contribuables", response_model=List[dict])
def get_contribuables_for_map(
    actif: Optional[bool] = True,
    db: Session = Depends(get_db)
):
    """
    Récupère les contribuables avec leurs coordonnées GPS pour affichage sur carte
    """
    from database.models import Contribuable
    from sqlalchemy.orm import joinedload
    
    query = db.query(Contribuable).options(
        joinedload(Contribuable.type_contribuable),
        joinedload(Contribuable.quartier),
        joinedload(Contribuable.collecteur)
    )
    
    if actif is not None:
        query = query.filter(Contribuable.actif == actif)
    
    # Filtrer uniquement ceux qui ont des coordonnées GPS
    query = query.filter(
        Contribuable.latitude.isnot(None),
        Contribuable.longitude.isnot(None)
    )
    
    contribuables = query.all()
    
    result = []
    for contrib in contribuables:
        result.append({
            "id": contrib.id,
            "nom": contrib.nom,
            "prenom": contrib.prenom,
            "nom_activite": contrib.nom_activite,
            "telephone": contrib.telephone,
            "adresse": contrib.adresse,
            "latitude": float(contrib.latitude) if contrib.latitude else None,
            "longitude": float(contrib.longitude) if contrib.longitude else None,
            "photo_url": contrib.photo_url,
            "type_contribuable": contrib.type_contribuable.nom if contrib.type_contribuable else None,
            "quartier": contrib.quartier.nom if contrib.quartier else None,
            "zone": contrib.quartier.zone.nom if contrib.quartier and contrib.quartier.zone else None,
            "collecteur": contrib.collecteur.nom + " " + contrib.collecteur.prenom if contrib.collecteur else None,
            "actif": contrib.actif
        })
    
    return result


@router.get("/uncovered-zones", response_model=List[dict])
def get_uncovered_zones(
    type_zone: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Identifie les zones géographiques sans contribuables (zones non couvertes)
    """
    from database.models import Contribuable, ZoneGeographique
    from sqlalchemy import and_
    
    query = (
        db.query(
            ZoneGeographique,
            func.count(Contribuable.id).label("contrib_count")
        )
        .outerjoin(
            Contribuable,
            and_(
                Contribuable.geom.isnot(None),
                Contribuable.actif == True,
                func.ST_Contains(ZoneGeographique.geom, Contribuable.geom)
            )
        )
        .filter(
            ZoneGeographique.actif == True,
            ZoneGeographique.geom.isnot(None)
        )
        .group_by(ZoneGeographique.id)
    )
    
    if type_zone:
        query = query.filter(ZoneGeographique.type_zone == type_zone)
    
    uncovered_zones = []
    for zone, contrib_count in query.all():
        if contrib_count == 0:
            uncovered_zones.append({
                "id": zone.id,
                "nom": zone.nom,
                "type_zone": zone.type_zone,
                "code": zone.code,
                "geometry": zone.geometry,
                "quartier_id": zone.quartier_id,
                "contribuables_count": 0
            })
    
    return uncovered_zones


@router.get("/map/collecteurs", response_model=List[dict])
def get_collecteurs_for_map(
    actif: Optional[bool] = True,
    db: Session = Depends(get_db)
):
    """
    Récupère les collecteurs avec leurs positions GPS pour affichage sur carte
    """
    from database.models import Collecteur
    
    query = db.query(Collecteur)
    
    if actif is not None:
        query = query.filter(Collecteur.actif == actif)
    
    # Filtrer uniquement ceux qui ont des coordonnées GPS
    query = query.filter(
        Collecteur.latitude.isnot(None),
        Collecteur.longitude.isnot(None)
    )
    
    collecteurs = query.all()
    
    result = []
    for collecteur in collecteurs:
        result.append({
            "id": collecteur.id,
            "nom": collecteur.nom,
            "prenom": collecteur.prenom,
            "matricule": collecteur.matricule,
            "telephone": collecteur.telephone,
            "email": collecteur.email,
            "latitude": float(collecteur.latitude) if collecteur.latitude else None,
            "longitude": float(collecteur.longitude) if collecteur.longitude else None,
            "statut": collecteur.statut.value if collecteur.statut else None,
            "etat": collecteur.etat.value if collecteur.etat else None,
            "date_derniere_connexion": collecteur.date_derniere_connexion.isoformat() if collecteur.date_derniere_connexion else None,
            "actif": collecteur.actif
        })
    
    return result

