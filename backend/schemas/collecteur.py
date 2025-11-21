"""
Schémas Pydantic pour les collecteurs
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class CollecteurBase(BaseModel):
    nom: str = Field(..., max_length=100)
    prenom: str = Field(..., max_length=100)
    email: EmailStr
    telephone: str = Field(..., max_length=20)
    matricule: str = Field(..., max_length=50)
    zone_id: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    heure_cloture: Optional[str] = Field(None, pattern=r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$')


class CollecteurCreate(CollecteurBase):
    pass


class CollecteurUpdate(BaseModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    email: Optional[EmailStr] = None
    telephone: Optional[str] = None
    zone_id: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    heure_cloture: Optional[str] = None
    statut: Optional[str] = None  # "active", "desactive"
    actif: Optional[bool] = None


class CollecteurResponse(CollecteurBase):
    id: int
    statut: str
    etat: str
    date_derniere_connexion: Optional[datetime] = None
    date_derniere_deconnexion: Optional[datetime] = None
    actif: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

