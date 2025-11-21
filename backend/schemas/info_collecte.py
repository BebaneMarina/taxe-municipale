"""
Schémas Pydantic pour les collectes
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal
from schemas.contribuable import ContribuableBase
from schemas.taxe import TaxeBase
from schemas.collecteur import CollecteurBase


class InfoCollecteBase(BaseModel):
    contribuable_id: int
    taxe_id: int
    collecteur_id: int
    montant: Decimal = Field(..., ge=0)
    type_paiement: str  # "especes", "mobile_money", "carte"
    billetage: Optional[str] = None  # JSON string
    date_collecte: datetime = Field(default_factory=datetime.utcnow)


class InfoCollecteCreate(InfoCollecteBase):
    pass


class InfoCollecteUpdate(BaseModel):
    statut: Optional[str] = None  # "pending", "completed", "failed", "cancelled"
    annule: Optional[bool] = None
    raison_annulation: Optional[str] = None
    sms_envoye: Optional[bool] = None
    ticket_imprime: Optional[bool] = None


class InfoCollecteResponse(InfoCollecteBase):
    id: int
    commission: Decimal
    statut: str
    reference: str
    date_cloture: Optional[datetime] = None
    sms_envoye: bool
    ticket_imprime: bool
    annule: bool
    raison_annulation: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    contribuable: Optional[ContribuableBase] = None
    taxe: Optional[TaxeBase] = None
    collecteur: Optional[CollecteurBase] = None

    class Config:
        from_attributes = True

