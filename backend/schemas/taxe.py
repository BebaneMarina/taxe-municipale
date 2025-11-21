"""
Schémas Pydantic pour les taxes
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal
from schemas.type_taxe import TypeTaxeBase
from schemas.service import ServiceBase


class TaxeBase(BaseModel):
    nom: str = Field(..., max_length=100)
    code: str = Field(..., max_length=20)
    description: Optional[str] = None
    montant: Decimal = Field(..., ge=0)
    montant_variable: bool = False
    periodicite: str  # "journaliere", "hebdomadaire", "mensuelle", "trimestrielle"
    type_taxe_id: int
    service_id: int
    commission_pourcentage: Decimal = Field(default=0.00, ge=0, le=100)
    actif: bool = True


class TaxeCreate(TaxeBase):
    pass


class TaxeUpdate(BaseModel):
    nom: Optional[str] = None
    description: Optional[str] = None
    montant: Optional[Decimal] = None
    montant_variable: Optional[bool] = None
    periodicite: Optional[str] = None
    commission_pourcentage: Optional[Decimal] = None
    actif: Optional[bool] = None


class TaxeResponse(TaxeBase):
    id: int
    type_taxe: Optional[TypeTaxeBase] = None
    service: Optional[ServiceBase] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

