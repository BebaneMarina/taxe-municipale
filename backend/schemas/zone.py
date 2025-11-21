"""
Schémas Pydantic pour les zones
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ZoneBase(BaseModel):
    nom: str = Field(..., max_length=100)
    code: str = Field(..., max_length=20)
    description: Optional[str] = None
    actif: bool = True


class ZoneCreate(ZoneBase):
    pass


class ZoneResponse(ZoneBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

