"""
Routes pour la gestion de la géolocalisation
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import InfoCollecte, Collecteur, CollecteLocation, CollecteurZone
from schemas.geolocalisation import LocationCreate, LocationResponse, ZoneResponse
from auth.security import get_current_active_user
from datetime import datetime

router = APIRouter(
    prefix="/api",
    tags=["geolocalisation"],
    dependencies=[Depends(get_current_active_user)],
)


@router.post("/collectes/{collecte_id}/location", response_model=LocationResponse, status_code=201)
def save_collecte_location(
    collecte_id: int,
    location_data: LocationCreate,
    db: Session = Depends(get_db),
):
    """
    Enregistrer la position GPS d'une collecte
    """
    # Vérifier que la collecte existe
    collecte = db.query(InfoCollecte).filter(InfoCollecte.id == collecte_id).first()
    if not collecte:
        raise HTTPException(status_code=404, detail="Collecte non trouvée")
    
    # Créer ou mettre à jour la position
    existing_location = db.query(CollecteLocation).filter(
        CollecteLocation.collecte_id == collecte_id
    ).first()
    
    if existing_location:
        # Mettre à jour
        existing_location.latitude = location_data.latitude
        existing_location.longitude = location_data.longitude
        existing_location.accuracy = location_data.accuracy
        existing_location.altitude = location_data.altitude
        existing_location.heading = location_data.heading
        existing_location.speed = location_data.speed
        existing_location.timestamp = location_data.timestamp or datetime.utcnow()
        existing_location.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing_location)
        return existing_location
    else:
        # Créer
        new_location = CollecteLocation(
            collecte_id=collecte_id,
            latitude=location_data.latitude,
            longitude=location_data.longitude,
            accuracy=location_data.accuracy,
            altitude=location_data.altitude,
            heading=location_data.heading,
            speed=location_data.speed,
            timestamp=location_data.timestamp or datetime.utcnow()
        )
        db.add(new_location)
        db.commit()
        db.refresh(new_location)
        return new_location


@router.get("/collectes/{collecte_id}/location", response_model=LocationResponse)
def get_collecte_location(
    collecte_id: int,
    db: Session = Depends(get_db),
):
    """
    Récupérer la position GPS d'une collecte
    """
    location = db.query(CollecteLocation).filter(
        CollecteLocation.collecte_id == collecte_id
    ).first()
    
    if not location:
        raise HTTPException(status_code=404, detail="Position non trouvée pour cette collecte")
    
    return location


@router.get("/collecteurs/{collecteur_id}/zones", response_model=list[ZoneResponse])
def get_collecteur_zones(
    collecteur_id: int,
    db: Session = Depends(get_db),
):
    """
    Récupérer les zones autorisées d'un collecteur
    """
    # Vérifier que le collecteur existe
    collecteur = db.query(Collecteur).filter(Collecteur.id == collecteur_id).first()
    if not collecteur:
        raise HTTPException(status_code=404, detail="Collecteur non trouvé")
    
    zones = db.query(CollecteurZone).filter(
        CollecteurZone.collecteur_id == collecteur_id,
        CollecteurZone.actif == True  # noqa: E712
    ).all()
    
    return zones

