"""
Routes pour les données de référence (zones, quartiers, types, services)
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database.database import get_db
from database.models import Zone, Quartier, TypeContribuable, TypeTaxe, Service
from schemas.zone import ZoneResponse
from schemas.quartier import QuartierResponse
from schemas.type_contribuable import TypeContribuableResponse
from schemas.type_taxe import TypeTaxeResponse
from schemas.service import ServiceResponse

router = APIRouter(prefix="/api/references", tags=["references"])


@router.get("/zones", response_model=List[ZoneResponse])
def get_zones(actif: Optional[bool] = None, db: Session = Depends(get_db)):
    """Récupère la liste des zones"""
    query = db.query(Zone)
    if actif is not None:
        query = query.filter(Zone.actif == actif)
    return query.all()


@router.get("/quartiers", response_model=List[QuartierResponse])
def get_quartiers(
    zone_id: Optional[int] = None,
    actif: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Récupère la liste des quartiers avec leurs zones"""
    from sqlalchemy.orm import joinedload
    
    query = db.query(Quartier).options(joinedload(Quartier.zone))
    if zone_id:
        query = query.filter(Quartier.zone_id == zone_id)
    if actif is not None:
        query = query.filter(Quartier.actif == actif)
    return query.all()


@router.get("/types-contribuables", response_model=List[TypeContribuableResponse])
def get_types_contribuables(actif: Optional[bool] = None, db: Session = Depends(get_db)):
    """Récupère la liste des types de contribuables"""
    query = db.query(TypeContribuable)
    if actif is not None:
        query = query.filter(TypeContribuable.actif == actif)
    return query.all()


@router.get("/types-taxes", response_model=List[TypeTaxeResponse])
def get_types_taxes(actif: Optional[bool] = None, db: Session = Depends(get_db)):
    """Récupère la liste des types de taxes"""
    query = db.query(TypeTaxe)
    if actif is not None:
        query = query.filter(TypeTaxe.actif == actif)
    return query.all()


@router.get("/services", response_model=List[ServiceResponse])
def get_services(actif: Optional[bool] = None, db: Session = Depends(get_db)):
    """Récupère la liste des services"""
    query = db.query(Service)
    if actif is not None:
        query = query.filter(Service.actif == actif)
    return query.all()

