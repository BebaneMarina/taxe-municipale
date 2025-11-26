"""
Schémas Pydantic pour le paramétrage des coupures de caisse
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field


class CoupureBase(BaseModel):
    valeur: Decimal = Field(..., gt=0, description="Valeur faciale de la coupure")
    devise: str = Field("XAF", min_length=3, max_length=3, description="Code devise (ex: XAF)")
    type_coupure: str = Field("billet", description="Type de coupure: billet ou piece")
    description: Optional[str] = Field(None, max_length=255)
    ordre_affichage: Optional[int] = Field(None, ge=0, description="Ordre d'affichage")
    actif: bool = True


class CoupureCreate(CoupureBase):
    pass


class CoupureUpdate(BaseModel):
    valeur: Optional[Decimal] = Field(None, gt=0)
    devise: Optional[str] = Field(None, min_length=3, max_length=3)
    type_coupure: Optional[str] = None
    description: Optional[str] = Field(None, max_length=255)
    ordre_affichage: Optional[int] = Field(None, ge=0)
    actif: Optional[bool] = None


class CoupureResponse(CoupureBase):
    id: int
    ordre_affichage: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CoupuresListResponse(BaseModel):
    items: List[CoupureResponse]
    total: int
    skip: int
    limit: int

