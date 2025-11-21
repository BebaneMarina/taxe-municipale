"""
Schémas Pydantic pour les types de taxes
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TypeTaxeBase(BaseModel):
    nom: str = Field(..., max_length=100)
    code: str = Field(..., max_length=20)
    description: Optional[str] = None
    actif: bool = True


class TypeTaxeCreate(TypeTaxeBase):
    pass


class TypeTaxeResponse(TypeTaxeBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

