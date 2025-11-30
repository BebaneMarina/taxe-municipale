"""
Schémas Pydantic pour les endpoints de notifications
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class TokenRegister(BaseModel):
    """Schéma pour enregistrer un token FCM"""
    token: str = Field(..., max_length=500, description="Token FCM")
    platform: str = Field(..., max_length=50, description="Plateforme: 'mobile', 'web', etc.")


class TokenResponse(BaseModel):
    """Réponse pour un token enregistré"""
    id: int
    user_id: int
    token: str
    platform: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotificationResponse(BaseModel):
    """Réponse pour une notification"""
    id: int
    user_id: int
    type: str
    title: str
    message: str
    read: bool
    data: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationCreate(BaseModel):
    """Schéma pour créer une notification"""
    user_id: int
    type: str = Field(..., max_length=50, description="Type: 'collecte', 'cloture', 'alerte', etc.")
    title: str = Field(..., max_length=255)
    message: str
    data: Optional[Dict[str, Any]] = None


class NotificationCountResponse(BaseModel):
    """Réponse pour le nombre de notifications non lues"""
    count: int

