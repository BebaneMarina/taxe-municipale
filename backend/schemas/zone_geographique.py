"""
Schémas Pydantic pour les zones géographiques
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class ZoneGeographiqueBase(BaseModel):
    nom: str = Field(..., max_length=100)
    type_zone: str = Field(..., max_length=50)  # 'quartier', 'arrondissement', 'secteur'
    code: Optional[str] = Field(None, max_length=50)
    geometry: Dict[str, Any] = Field(..., description="GeoJSON geometry (Polygon ou MultiPolygon)")
    properties: Optional[Dict[str, Any]] = None
    quartier_id: Optional[int] = None
    actif: bool = True


class ZoneGeographiqueCreate(ZoneGeographiqueBase):
    pass


class ZoneGeographiqueUpdate(BaseModel):
    nom: Optional[str] = None
    type_zone: Optional[str] = None
    code: Optional[str] = None
    geometry: Optional[Dict[str, Any]] = None
    properties: Optional[Dict[str, Any]] = None
    quartier_id: Optional[int] = None
    actif: Optional[bool] = None


class ZoneGeographiqueResponse(ZoneGeographiqueBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PointLocationRequest(BaseModel):
    """Requête pour déterminer la zone d'un point GPS"""
    latitude: float = Field(..., description="Latitude du point")
    longitude: float = Field(..., description="Longitude du point")
    type_zone: Optional[str] = Field(None, description="Type de zone recherché (quartier, arrondissement, secteur)")


class PointLocationResponse(BaseModel):
    """Réponse avec la zone trouvée pour un point GPS"""
    zone: Optional[ZoneGeographiqueResponse] = None
    found: bool
    message: str

