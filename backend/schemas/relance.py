"""
Schémas Pydantic pour les relances
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from schemas.contribuable import ContribuableBase
from schemas.affectation_taxe import AffectationTaxeBase


class RelanceBase(BaseModel):
    contribuable_id: int
    affectation_taxe_id: Optional[int] = None
    type_relance: str  # sms, email, appel, courrier, visite
    message: Optional[str] = None
    montant_due: Decimal
    date_echeance: Optional[datetime] = None
    date_planifiee: datetime
    canal_envoi: Optional[str] = None
    notes: Optional[str] = None


class RelanceCreate(RelanceBase):
    utilisateur_id: Optional[int] = None


class RelanceUpdate(BaseModel):
    statut: Optional[str] = None
    date_envoi: Optional[datetime] = None
    reponse_recue: Optional[bool] = None
    date_reponse: Optional[datetime] = None
    notes: Optional[str] = None


class RelanceResponse(RelanceBase):
    id: int
    statut: str
    date_envoi: Optional[datetime] = None
    reponse_recue: bool
    date_reponse: Optional[datetime] = None
    utilisateur_id: Optional[int] = None
    contribuable: Optional[ContribuableBase] = None
    affectation_taxe: Optional[AffectationTaxeBase] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RelanceListResponse(BaseModel):
    items: List[RelanceResponse]
    total: int
    skip: int
    limit: int


class RelanceManuelleItem(BaseModel):
    contribuable_id: int
    telephone_override: Optional[str] = None
    montant_due: Optional[Decimal] = None
    date_echeance: Optional[datetime] = None
    message: Optional[str] = None
    notes: Optional[str] = None


class RelanceManuelleRequest(BaseModel):
    type_relance: str
    message: Optional[str] = None
    montant_due: Optional[Decimal] = None
    date_echeance: Optional[datetime] = None
    date_planifiee: Optional[datetime] = None
    utilisateur_id: Optional[int] = None
    notes: Optional[str] = None
    contribuables: List[RelanceManuelleItem] = Field(..., min_length=1)
