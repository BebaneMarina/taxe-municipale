"""
Routes pour la gestion des taxes
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database.database import get_db
from database.models import Taxe
from schemas.taxe import TaxeCreate, TaxeUpdate, TaxeResponse
from datetime import datetime

router = APIRouter(prefix="/api/taxes", tags=["taxes"])


@router.get("/", response_model=List[TaxeResponse])
def get_taxes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    actif: Optional[bool] = None,
    type_taxe_id: Optional[int] = None,
    service_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Récupère la liste des taxes avec filtres"""
    query = db.query(Taxe)
    
    if actif is not None:
        query = query.filter(Taxe.actif == actif)
    if type_taxe_id:
        query = query.filter(Taxe.type_taxe_id == type_taxe_id)
    if service_id:
        query = query.filter(Taxe.service_id == service_id)
    
    taxes = query.offset(skip).limit(limit).all()
    return taxes


@router.get("/{taxe_id}", response_model=TaxeResponse)
def get_taxe(taxe_id: int, db: Session = Depends(get_db)):
    """Récupère une taxe par son ID"""
    taxe = db.query(Taxe).filter(Taxe.id == taxe_id).first()
    if not taxe:
        raise HTTPException(status_code=404, detail="Taxe non trouvée")
    return taxe


@router.post("/", response_model=TaxeResponse, status_code=201)
def create_taxe(taxe: TaxeCreate, db: Session = Depends(get_db)):
    """Crée une nouvelle taxe"""
    # Vérifier si le code existe déjà
    existing = db.query(Taxe).filter(Taxe.code == taxe.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Une taxe avec ce code existe déjà")
    
    db_taxe = Taxe(**taxe.dict())
    db.add(db_taxe)
    db.commit()
    db.refresh(db_taxe)
    return db_taxe


@router.put("/{taxe_id}", response_model=TaxeResponse)
def update_taxe(taxe_id: int, taxe_update: TaxeUpdate, db: Session = Depends(get_db)):
    """Met à jour une taxe"""
    db_taxe = db.query(Taxe).filter(Taxe.id == taxe_id).first()
    if not db_taxe:
        raise HTTPException(status_code=404, detail="Taxe non trouvée")
    
    update_data = taxe_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_taxe, field, value)
    
    db_taxe.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_taxe)
    return db_taxe


@router.delete("/{taxe_id}", status_code=204)
def delete_taxe(taxe_id: int, db: Session = Depends(get_db)):
    """Supprime une taxe (soft delete)"""
    db_taxe = db.query(Taxe).filter(Taxe.id == taxe_id).first()
    if not db_taxe:
        raise HTTPException(status_code=404, detail="Taxe non trouvée")
    
    db_taxe.actif = False
    db_taxe.updated_at = datetime.utcnow()
    db.commit()
    return None

