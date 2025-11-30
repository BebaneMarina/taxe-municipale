"""
Schémas Pydantic pour les endpoints de géolocalisation
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class LocationCreate(BaseModel):
    """Schéma pour créer/enregistrer une position GPS"""
    latitude: Decimal = Field(..., description="Latitude")
    longitude: Decimal = Field(..., description="Longitude")
    accuracy: Optional[Decimal] = Field(None, description="Précision en mètres")
    altitude: Optional[Decimal] = Field(None, description="Altitute en mètres")
    heading: Optional[Decimal] = Field(None, description="Direction en degrés (0-360)")
    speed: Optional[Decimal] = Field(None, description="Vitesse en m/s")
    timestamp: Optional[datetime] = Field(None, description="Timestamp de la position")


class LocationResponse(BaseModel):
    """Réponse pour une position GPS"""
    id: int
    collecte_id: int
    latitude: Decimal
    longitude: Decimal
    accuracy: Optional[Decimal] = None
    altitude: Optional[Decimal] = None
    heading: Optional[Decimal] = None
    speed: Optional[Decimal] = None
    timestamp: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ZoneResponse(BaseModel):
    """Réponse pour une zone autorisée d'un collecteur"""
    id: int
    collecteur_id: int
    nom: str
    latitude: Decimal
    longitude: Decimal
    radius: Decimal
    description: Optional[str] = None
    actif: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ZoneCreate(BaseModel):
    """Schéma pour créer une zone autorisée"""
    nom: str = Field(..., max_length=255)
    latitude: Decimal = Field(..., description="Latitude du centre")
    longitude: Decimal = Field(..., description="Longitude du centre")
    radius: Decimal = Field(default=1000.0, description="Rayon en mètres")
    description: Optional[str] = None
    actif: bool = True

