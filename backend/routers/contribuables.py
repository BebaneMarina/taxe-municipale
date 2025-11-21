"""
Routes pour la gestion des contribuables
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from database.database import get_db
from database.models import Contribuable
from schemas.contribuable import ContribuableCreate, ContribuableUpdate, ContribuableResponse
from datetime import datetime

router = APIRouter(prefix="/api/contribuables", tags=["contribuables"])


def make_point(longitude: Optional[float], latitude: Optional[float]):
    if longitude is None or latitude is None:
        return None
    return func.ST_SetSRID(func.ST_MakePoint(longitude, latitude), 4326)


@router.get("/", response_model=List[ContribuableResponse])
def get_contribuables(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    actif: Optional[bool] = None,
    collecteur_id: Optional[int] = None,
    quartier_id: Optional[int] = None,
    type_contribuable_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Récupère la liste des contribuables avec filtres et relations"""
    from sqlalchemy.orm import joinedload
    
    # Query de base avec relations (incluant la zone du quartier)
    from database.models import Quartier, Zone
    query = db.query(Contribuable).options(
        joinedload(Contribuable.type_contribuable),
        joinedload(Contribuable.quartier).joinedload(Quartier.zone),
        joinedload(Contribuable.collecteur)
    )
    
    # Query pour compter le total (sans les relations pour la performance)
    count_query = db.query(func.count(Contribuable.id))
    
    # Appliquer les mêmes filtres aux deux queries
    if actif is not None:
        query = query.filter(Contribuable.actif == actif)
        count_query = count_query.filter(Contribuable.actif == actif)
    if collecteur_id:
        query = query.filter(Contribuable.collecteur_id == collecteur_id)
        count_query = count_query.filter(Contribuable.collecteur_id == collecteur_id)
    if quartier_id:
        query = query.filter(Contribuable.quartier_id == quartier_id)
        count_query = count_query.filter(Contribuable.quartier_id == quartier_id)
    if type_contribuable_id:
        query = query.filter(Contribuable.type_contribuable_id == type_contribuable_id)
        count_query = count_query.filter(Contribuable.type_contribuable_id == type_contribuable_id)
    if search:
        search_term = f"%{search}%"
        search_filter = (
            (Contribuable.nom.ilike(search_term)) |
            (Contribuable.prenom.ilike(search_term)) |
            (Contribuable.telephone.ilike(search_term)) |
            (Contribuable.numero_identification.ilike(search_term))
        )
        query = query.filter(search_filter)
        count_query = count_query.filter(search_filter)
    
    # Récupérer les résultats
    contribuables = query.offset(skip).limit(limit).all()
    
    # Note: Le total n'est pas retourné dans la réponse car on utilise List[ContribuableResponse]
    # Pour avoir le total, il faudrait créer un schéma de réponse avec pagination
    # Pour l'instant, on retourne juste la liste
    return contribuables


@router.get("/{contribuable_id}", response_model=ContribuableResponse)
def get_contribuable(contribuable_id: int, db: Session = Depends(get_db)):
    """Récupère un contribuable par son ID avec toutes les relations"""
    from sqlalchemy.orm import joinedload
    from database.models import Quartier
    
    contribuable = db.query(Contribuable).options(
        joinedload(Contribuable.type_contribuable),
        joinedload(Contribuable.quartier).joinedload(Quartier.zone),
        joinedload(Contribuable.collecteur)
    ).filter(Contribuable.id == contribuable_id).first()
    
    if not contribuable:
        raise HTTPException(status_code=404, detail="Contribuable non trouvé")
    return contribuable


@router.post("/", response_model=ContribuableResponse, status_code=201)
def create_contribuable(contribuable: ContribuableCreate, db: Session = Depends(get_db)):
    """Crée un nouveau contribuable"""
    from sqlalchemy.orm import joinedload
    
    # Vérifier si le téléphone existe déjà
    existing = db.query(Contribuable).filter(Contribuable.telephone == contribuable.telephone).first()
    if existing:
        raise HTTPException(status_code=400, detail="Un contribuable avec ce téléphone existe déjà")
    
    # Vérifier si le numéro d'identification existe déjà (si fourni)
    if contribuable.numero_identification:
        existing_id = db.query(Contribuable).filter(Contribuable.numero_identification == contribuable.numero_identification).first()
        if existing_id:
            raise HTTPException(status_code=400, detail="Un contribuable avec ce numéro d'identification existe déjà")
    
    # Détection automatique de zone si GPS disponible
    quartier_id = contribuable.quartier_id
    geom_point = make_point(contribuable.longitude, contribuable.latitude)
    if geom_point is not None:
        from database.models import ZoneGeographique
        zone_match = db.query(ZoneGeographique).filter(
            ZoneGeographique.actif == True,
            ZoneGeographique.geom.isnot(None),
            ZoneGeographique.type_zone == 'quartier',
            func.ST_Contains(ZoneGeographique.geom, geom_point)
        ).first()
        if zone_match and zone_match.quartier_id:
            quartier_id = zone_match.quartier_id
    
    # Créer le contribuable avec le quartier_id (détecté ou fourni)
    contribuable_dict = contribuable.dict()
    contribuable_dict['quartier_id'] = quartier_id
    db_contribuable = Contribuable(**contribuable_dict)
    if geom_point is not None:
        db_contribuable.geom = geom_point
    db.add(db_contribuable)
    db.commit()
    db.refresh(db_contribuable)
    
    # Recharger avec les relations (incluant la zone du quartier)
    from database.models import Quartier
    db_contribuable = db.query(Contribuable).options(
        joinedload(Contribuable.type_contribuable),
        joinedload(Contribuable.quartier).joinedload(Quartier.zone),
        joinedload(Contribuable.collecteur)
    ).filter(Contribuable.id == db_contribuable.id).first()
    
    return db_contribuable


@router.put("/{contribuable_id}", response_model=ContribuableResponse)
def update_contribuable(contribuable_id: int, contribuable_update: ContribuableUpdate, db: Session = Depends(get_db)):
    """Met à jour un contribuable"""
    from sqlalchemy.orm import joinedload
    
    db_contribuable = db.query(Contribuable).filter(Contribuable.id == contribuable_id).first()
    if not db_contribuable:
        raise HTTPException(status_code=404, detail="Contribuable non trouvé")
    
    # Vérifier si le téléphone existe déjà (si modifié)
    if contribuable_update.telephone and contribuable_update.telephone != db_contribuable.telephone:
        existing = db.query(Contribuable).filter(Contribuable.telephone == contribuable_update.telephone).first()
        if existing:
            raise HTTPException(status_code=400, detail="Un contribuable avec ce téléphone existe déjà")
    
    # Vérifier si le numéro d'identification existe déjà (si modifié)
    if contribuable_update.numero_identification and contribuable_update.numero_identification != db_contribuable.numero_identification:
        existing_id = db.query(Contribuable).filter(Contribuable.numero_identification == contribuable_update.numero_identification).first()
        if existing_id:
            raise HTTPException(status_code=400, detail="Un contribuable avec ce numéro d'identification existe déjà")
    
    update_data = contribuable_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_contribuable, field, value)
    
    if "latitude" in update_data or "longitude" in update_data:
        geom_point = make_point(db_contribuable.longitude, db_contribuable.latitude)
        db_contribuable.geom = geom_point
        if geom_point is not None:
            from database.models import ZoneGeographique
            zone_match = db.query(ZoneGeographique).filter(
                ZoneGeographique.actif == True,
                ZoneGeographique.geom.isnot(None),
                ZoneGeographique.type_zone == 'quartier',
                func.ST_Contains(ZoneGeographique.geom, geom_point)
            ).first()
            if zone_match and zone_match.quartier_id:
                db_contribuable.quartier_id = zone_match.quartier_id
    
    db_contribuable.updated_at = datetime.utcnow()
    db.commit()
    
    # Recharger avec les relations (incluant la zone du quartier)
    from sqlalchemy.orm import joinedload
    from database.models import Quartier
    db_contribuable = db.query(Contribuable).options(
        joinedload(Contribuable.type_contribuable),
        joinedload(Contribuable.quartier).joinedload(Quartier.zone),
        joinedload(Contribuable.collecteur)
    ).filter(Contribuable.id == contribuable_id).first()
    
    return db_contribuable


@router.patch("/{contribuable_id}/transfert", response_model=ContribuableResponse)
def transfert_contribuable(
    contribuable_id: int,
    nouveau_collecteur_id: int = Query(..., description="ID du nouveau collecteur"),
    db: Session = Depends(get_db)
):
    """Transfère un contribuable à un autre collecteur"""
    from sqlalchemy.orm import joinedload
    
    db_contribuable = db.query(Contribuable).filter(Contribuable.id == contribuable_id).first()
    if not db_contribuable:
        raise HTTPException(status_code=404, detail="Contribuable non trouvé")
    
    # Vérifier que le nouveau collecteur existe
    from database.models import Collecteur
    nouveau_collecteur = db.query(Collecteur).filter(Collecteur.id == nouveau_collecteur_id).first()
    if not nouveau_collecteur:
        raise HTTPException(status_code=404, detail="Collecteur non trouvé")
    
    if nouveau_collecteur.statut.value != 'active':
        raise HTTPException(status_code=400, detail="Le collecteur cible n'est pas actif")
    
    ancien_collecteur_id = db_contribuable.collecteur_id
    db_contribuable.collecteur_id = nouveau_collecteur_id
    db_contribuable.updated_at = datetime.utcnow()
    
    # TODO: Historiser le transfert
    
    db.commit()
    
    # Recharger avec les relations (incluant la zone du quartier)
    from sqlalchemy.orm import joinedload
    from database.models import Quartier
    db_contribuable = db.query(Contribuable).options(
        joinedload(Contribuable.type_contribuable),
        joinedload(Contribuable.quartier).joinedload(Quartier.zone),
        joinedload(Contribuable.collecteur)
    ).filter(Contribuable.id == contribuable_id).first()
    
    return db_contribuable


@router.delete("/{contribuable_id}", status_code=204)
def delete_contribuable(contribuable_id: int, db: Session = Depends(get_db)):
    """Supprime un contribuable (soft delete)"""
    db_contribuable = db.query(Contribuable).filter(Contribuable.id == contribuable_id).first()
    if not db_contribuable:
        raise HTTPException(status_code=404, detail="Contribuable non trouvé")
    
    db_contribuable.actif = False
    db_contribuable.updated_at = datetime.utcnow()
    db.commit()
    return None

