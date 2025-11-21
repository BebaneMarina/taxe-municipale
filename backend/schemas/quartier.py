"""
Schémas Pydantic pour les quartiers
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from schemas.zone import ZoneBase


class QuartierBase(BaseModel):
    nom: str = Field(..., max_length=100)
    code: str = Field(..., max_length=20)
    zone_id: int
    description: Optional[str] = None
    actif: bool = True


class QuartierCreate(QuartierBase):
    pass


class QuartierResponse(QuartierBase):
    id: int
    zone: Optional[ZoneBase] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

