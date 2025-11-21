"""
Schémas Pydantic pour l'authentification
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Optional[dict] = None


class TokenData(BaseModel):
    user_id: Optional[int] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserCreate(BaseModel):
    nom: str = Field(..., max_length=100)
    prenom: str = Field(..., max_length=100)
    email: EmailStr
    telephone: Optional[str] = Field(None, max_length=20)
    password: str = Field(..., min_length=6)
    role: str = Field(default="agent_back_office")  # admin, agent_back_office, agent_front_office, controleur_interne, collecteur


class UserUpdate(BaseModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    email: Optional[EmailStr] = None
    telephone: Optional[str] = None
    role: Optional[str] = None
    actif: Optional[bool] = None


class UserChangePassword(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6)


class UserResponse(BaseModel):
    id: int
    nom: str
    prenom: str
    email: str
    telephone: Optional[str]
    role: str
    actif: bool
    derniere_connexion: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

