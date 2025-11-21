"""
Schémas Pydantic pour les affectations de taxes
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal
from schemas.contribuable import ContribuableBase
from schemas.taxe import TaxeBase


class AffectationTaxeBase(BaseModel):
    contribuable_id: int
    taxe_id: int
    date_debut: datetime
    date_fin: Optional[datetime] = None
    montant_custom: Optional[Decimal] = None
    actif: bool = True


class AffectationTaxeCreate(AffectationTaxeBase):
    pass


class AffectationTaxeUpdate(BaseModel):
    date_fin: Optional[datetime] = None
    montant_custom: Optional[Decimal] = None
    actif: Optional[bool] = None


class AffectationTaxeResponse(AffectationTaxeBase):
    id: int
    contribuable: Optional[ContribuableBase] = None
    taxe: Optional[TaxeBase] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

