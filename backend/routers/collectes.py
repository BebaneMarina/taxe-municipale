"""
Routes pour la gestion des collectes
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database.database import get_db
from database.models import InfoCollecte, Taxe, StatutCollecteEnum
from schemas.info_collecte import InfoCollecteCreate, InfoCollecteUpdate, InfoCollecteResponse
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, Field
from auth.security import get_current_active_user

router = APIRouter(
    prefix="/api/collectes",
    tags=["collectes"],
    dependencies=[Depends(get_current_active_user)],
)


class CollecteAnnulationRequest(BaseModel):
    raison: str = Field(..., min_length=3, description="Raison de l'annulation")


@router.get("/", response_model=List[InfoCollecteResponse])
def get_collectes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    collecteur_id: Optional[int] = None,
    contribuable_id: Optional[int] = None,
    taxe_id: Optional[int] = None,
    statut: Optional[str] = None,
    date_debut: Optional[date] = None,
    date_fin: Optional[date] = None,
    telephone: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Récupère la liste des collectes avec filtres et relations"""
    from sqlalchemy.orm import joinedload
    from database.models import Contribuable
    
    from database.models import CollecteLocation
    
    query = db.query(InfoCollecte).options(
        joinedload(InfoCollecte.contribuable),
        joinedload(InfoCollecte.taxe),
        joinedload(InfoCollecte.collecteur),
        joinedload(InfoCollecte.location)
    )
    
    if collecteur_id:
        query = query.filter(InfoCollecte.collecteur_id == collecteur_id)
    if contribuable_id:
        query = query.filter(InfoCollecte.contribuable_id == contribuable_id)
    if taxe_id:
        query = query.filter(InfoCollecte.taxe_id == taxe_id)
    if statut:
        try:
            statut_enum = StatutCollecteEnum(statut)
            query = query.filter(InfoCollecte.statut == statut_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail="Statut invalide")
    if date_debut:
        query = query.filter(InfoCollecte.date_collecte >= datetime.combine(date_debut, datetime.min.time()))
    if date_fin:
        query = query.filter(InfoCollecte.date_collecte <= datetime.combine(date_fin, datetime.max.time()))
    if telephone:
        # Filtrer par téléphone du contribuable
        query = query.join(Contribuable).filter(Contribuable.telephone.ilike(f"%{telephone}%"))
    
    collectes = query.order_by(InfoCollecte.date_collecte.desc()).offset(skip).limit(limit).all()
    return collectes


@router.get("/{collecte_id}", response_model=InfoCollecteResponse)
def get_collecte(collecte_id: int, db: Session = Depends(get_db)):
    """Récupère une collecte par son ID avec toutes les relations"""
    from sqlalchemy.orm import joinedload
    
    from database.models import CollecteLocation
    
    collecte = db.query(InfoCollecte).options(
        joinedload(InfoCollecte.contribuable),
        joinedload(InfoCollecte.taxe),
        joinedload(InfoCollecte.collecteur),
        joinedload(InfoCollecte.location)
    ).filter(InfoCollecte.id == collecte_id).first()
    
    if not collecte:
        raise HTTPException(status_code=404, detail="Collecte non trouvée")
    return collecte


@router.post("/", response_model=InfoCollecteResponse, status_code=201)
def create_collecte(collecte: InfoCollecteCreate, db: Session = Depends(get_db)):
    """Crée une nouvelle collecte"""
    # Récupérer la taxe pour calculer la commission
    taxe = db.query(Taxe).filter(Taxe.id == collecte.taxe_id).first()
    if not taxe:
        raise HTTPException(status_code=404, detail="Taxe non trouvée")
    
    # Calculer la commission
    commission = float(collecte.montant) * (float(taxe.commission_pourcentage) / 100)
    
    # Générer une référence unique
    reference = f"COL-{datetime.utcnow().strftime('%Y%m%d')}-{db.query(InfoCollecte).count() + 1:04d}"
    
    db_collecte = InfoCollecte(
        **collecte.dict(),
        commission=Decimal(str(commission)),
        reference=reference,
        statut=StatutCollecteEnum.PENDING
    )
    db.add(db_collecte)
    db.commit()
    db.refresh(db_collecte)
    return db_collecte


@router.put("/{collecte_id}", response_model=InfoCollecteResponse)
def update_collecte(collecte_id: int, collecte_update: InfoCollecteUpdate, db: Session = Depends(get_db)):
    """Met à jour une collecte"""
    db_collecte = db.query(InfoCollecte).filter(InfoCollecte.id == collecte_id).first()
    if not db_collecte:
        raise HTTPException(status_code=404, detail="Collecte non trouvée")
    
    update_data = collecte_update.dict(exclude_unset=True)
    
    # Gérer le statut
    if "statut" in update_data:
        try:
            update_data["statut"] = StatutCollecteEnum(update_data["statut"])
        except ValueError:
            raise HTTPException(status_code=400, detail="Statut invalide")
    
    for field, value in update_data.items():
        setattr(db_collecte, field, value)
    
    db_collecte.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_collecte)
    return db_collecte


@router.patch("/{collecte_id}/annuler", response_model=InfoCollecteResponse)
def annuler_collecte(
    collecte_id: int,
    payload: CollecteAnnulationRequest,
    db: Session = Depends(get_db)
):
    """Annule une collecte"""
    db_collecte = db.query(InfoCollecte).filter(InfoCollecte.id == collecte_id).first()
    if not db_collecte:
        raise HTTPException(status_code=404, detail="Collecte non trouvée")
    
    db_collecte.annule = True
    db_collecte.raison_annulation = payload.raison
    db_collecte.statut = StatutCollecteEnum.CANCELLED
    db_collecte.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_collecte)
    return db_collecte


@router.patch("/{collecte_id}/valider", response_model=InfoCollecteResponse)
def valider_collecte(collecte_id: int, db: Session = Depends(get_db)):
    """Valide une collecte et met à jour son statut"""
    db_collecte = db.query(InfoCollecte).filter(InfoCollecte.id == collecte_id).first()
    if not db_collecte:
        raise HTTPException(status_code=404, detail="Collecte non trouvée")

    if db_collecte.annule:
        raise HTTPException(status_code=400, detail="Impossible de valider une collecte annulée")

    db_collecte.statut = StatutCollecteEnum.COMPLETED
    db_collecte.date_cloture = datetime.utcnow()
    db_collecte.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_collecte)
    return db_collecte


@router.delete("/{collecte_id}", status_code=204)
def delete_collecte(collecte_id: int, db: Session = Depends(get_db)):
    """Supprime une collecte"""
    db_collecte = db.query(InfoCollecte).filter(InfoCollecte.id == collecte_id).first()
    if not db_collecte:
        raise HTTPException(status_code=404, detail="Collecte non trouvée")
    
    db.delete(db_collecte)
    db.commit()
    return None

