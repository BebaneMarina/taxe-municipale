"""
Routes pour la gestion des collecteurs
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from database.database import get_db
from database.models import Collecteur, StatutCollecteurEnum, EtatCollecteurEnum
from schemas.collecteur import CollecteurCreate, CollecteurUpdate, CollecteurResponse
from datetime import datetime

router = APIRouter(prefix="/api/collecteurs", tags=["collecteurs"])


def make_point(longitude: Optional[float], latitude: Optional[float]):
    if longitude is None or latitude is None:
        return None
    return func.ST_SetSRID(func.ST_MakePoint(longitude, latitude), 4326)


@router.get("/", response_model=List[CollecteurResponse])
def get_collecteurs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    statut: Optional[str] = None,
    etat: Optional[str] = None,
    zone_id: Optional[int] = None,
    actif: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Récupère la liste des collecteurs avec filtres"""
    query = db.query(Collecteur)
    
    if actif is not None:
        query = query.filter(Collecteur.actif == actif)
    if statut:
        try:
            statut_enum = StatutCollecteurEnum(statut)
            query = query.filter(Collecteur.statut == statut_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail="Statut invalide")
    if etat:
        try:
            etat_enum = EtatCollecteurEnum(etat)
            query = query.filter(Collecteur.etat == etat_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail="État invalide")
    if zone_id:
        query = query.filter(Collecteur.zone_id == zone_id)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Collecteur.nom.ilike(search_term)) |
            (Collecteur.prenom.ilike(search_term)) |
            (Collecteur.matricule.ilike(search_term)) |
            (Collecteur.email.ilike(search_term))
        )
    
    collecteurs = query.offset(skip).limit(limit).all()
    return collecteurs


@router.get("/{collecteur_id}", response_model=CollecteurResponse)
def get_collecteur(collecteur_id: int, db: Session = Depends(get_db)):
    """Récupère un collecteur par son ID"""
    collecteur = db.query(Collecteur).filter(Collecteur.id == collecteur_id).first()
    if not collecteur:
        raise HTTPException(status_code=404, detail="Collecteur non trouvé")
    return collecteur


@router.post("/", response_model=CollecteurResponse, status_code=201)
def create_collecteur(collecteur: CollecteurCreate, db: Session = Depends(get_db)):
    """Crée un nouveau collecteur"""
    # Vérifier si le matricule existe déjà
    existing = db.query(Collecteur).filter(Collecteur.matricule == collecteur.matricule).first()
    if existing:
        raise HTTPException(status_code=400, detail="Un collecteur avec ce matricule existe déjà")
    
    # Vérifier si l'email existe déjà
    existing_email = db.query(Collecteur).filter(Collecteur.email == collecteur.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Un collecteur avec cet email existe déjà")
    
    db_collecteur = Collecteur(
        **collecteur.dict(),
        statut=StatutCollecteurEnum.ACTIVE,
        etat=EtatCollecteurEnum.DECONNECTE
    )
    db.add(db_collecteur)
    db.commit()
    db.refresh(db_collecteur)
    return db_collecteur


@router.put("/{collecteur_id}", response_model=CollecteurResponse)
def update_collecteur(collecteur_id: int, collecteur_update: CollecteurUpdate, db: Session = Depends(get_db)):
    """Met à jour un collecteur"""
    db_collecteur = db.query(Collecteur).filter(Collecteur.id == collecteur_id).first()
    if not db_collecteur:
        raise HTTPException(status_code=404, detail="Collecteur non trouvé")
    
    update_data = collecteur_update.dict(exclude_unset=True)
    
    # Gérer le statut
    if "statut" in update_data:
        try:
            update_data["statut"] = StatutCollecteurEnum(update_data["statut"])
        except ValueError:
            raise HTTPException(status_code=400, detail="Statut invalide")
    
    for field, value in update_data.items():
        setattr(db_collecteur, field, value)
    
    if "latitude" in update_data or "longitude" in update_data:
        geom_point = make_point(db_collecteur.longitude, db_collecteur.latitude)
        db_collecteur.geom = geom_point
    
    db_collecteur.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_collecteur)
    return db_collecteur


@router.patch("/{collecteur_id}/position", response_model=CollecteurResponse)
def update_collecteur_position(
    collecteur_id: int,
    latitude: float,
    longitude: float,
    db: Session = Depends(get_db)
):
    """Met à jour la position GPS d'un collecteur (pour suivi en temps réel)"""
    db_collecteur = db.query(Collecteur).filter(Collecteur.id == collecteur_id).first()
    if not db_collecteur:
        raise HTTPException(status_code=404, detail="Collecteur non trouvé")
    
    from decimal import Decimal
    db_collecteur.latitude = Decimal(str(latitude))
    db_collecteur.longitude = Decimal(str(longitude))
    db_collecteur.geom = make_point(float(db_collecteur.longitude), float(db_collecteur.latitude))
    db_collecteur.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_collecteur)
    return db_collecteur


@router.patch("/{collecteur_id}/connexion", response_model=CollecteurResponse)
def connexion_collecteur(collecteur_id: int, db: Session = Depends(get_db)):
    """Connecte un collecteur"""
    db_collecteur = db.query(Collecteur).filter(Collecteur.id == collecteur_id).first()
    if not db_collecteur:
        raise HTTPException(status_code=404, detail="Collecteur non trouvé")
    
    if db_collecteur.statut != StatutCollecteurEnum.ACTIVE:
        raise HTTPException(status_code=400, detail="Le collecteur n'est pas actif")
    
    db_collecteur.etat = EtatCollecteurEnum.CONNECTE
    db_collecteur.date_derniere_connexion = datetime.utcnow()
    db_collecteur.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_collecteur)
    return db_collecteur


@router.patch("/{collecteur_id}/deconnexion", response_model=CollecteurResponse)
def deconnexion_collecteur(collecteur_id: int, db: Session = Depends(get_db)):
    """Déconnecte un collecteur"""
    db_collecteur = db.query(Collecteur).filter(Collecteur.id == collecteur_id).first()
    if not db_collecteur:
        raise HTTPException(status_code=404, detail="Collecteur non trouvé")
    
    db_collecteur.etat = EtatCollecteurEnum.DECONNECTE
    db_collecteur.date_derniere_deconnexion = datetime.utcnow()
    db_collecteur.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_collecteur)
    return db_collecteur


@router.delete("/{collecteur_id}", status_code=204)
def delete_collecteur(collecteur_id: int, db: Session = Depends(get_db)):
    """Supprime un collecteur (soft delete)"""
    db_collecteur = db.query(Collecteur).filter(Collecteur.id == collecteur_id).first()
    if not db_collecteur:
        raise HTTPException(status_code=404, detail="Collecteur non trouvé")
    
    db_collecteur.actif = False
    db_collecteur.statut = StatutCollecteurEnum.DESACTIVE
    db_collecteur.updated_at = datetime.utcnow()
    db.commit()
    return None

