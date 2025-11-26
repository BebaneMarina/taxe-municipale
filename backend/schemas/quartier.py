"""
Schémas Pydantic pour les quartiers
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from schemas.zone import ZoneBase


class QuartierBase(BaseModel):
    nom: str = Field(..., max_length=100)
    code: str = Field(..., max_length=20)
    zone_id: int
    description: Optional[str] = None
    actif: bool = True
    place_type: Optional[str] = Field(None, max_length=50)
    osm_id: Optional[int] = None
    tags: Optional[Dict[str, Any]] = None


class QuartierCreate(QuartierBase):
    pass


class QuartierResponse(QuartierBase):
    id: int
    zone: Optional[ZoneBase] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    geom_geojson: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

