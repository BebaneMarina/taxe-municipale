"""
Routes pour les données de référence (zones, quartiers, types, services)
"""

import json
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
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
    query = (
        db.query(
            Quartier,
            func.ST_AsGeoJSON(Quartier.geom).label("geom_geojson"),
            func.ST_X(Quartier.geom).label("longitude"),
            func.ST_Y(Quartier.geom).label("latitude"),
        )
        .options(joinedload(Quartier.zone))
    )
    if zone_id:
        query = query.filter(Quartier.zone_id == zone_id)
    if actif is not None:
        query = query.filter(Quartier.actif == actif)
    
    rows = query.order_by(Quartier.nom.asc()).all()
    result: List[QuartierResponse] = []
    for quartier, geom_geojson, longitude, latitude in rows:
        data = QuartierResponse(
            id=quartier.id,
            nom=quartier.nom,
            code=quartier.code,
            zone_id=quartier.zone_id,
            description=quartier.description,
            actif=quartier.actif,
            place_type=quartier.place_type,
            osm_id=quartier.osm_id,
            tags=quartier.tags,
            zone=quartier.zone,
            latitude=float(latitude) if latitude is not None else None,
            longitude=float(longitude) if longitude is not None else None,
            geom_geojson=json.loads(geom_geojson) if geom_geojson else None,
            created_at=quartier.created_at,
            updated_at=quartier.updated_at,
        )
        result.append(data)
    return result


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

