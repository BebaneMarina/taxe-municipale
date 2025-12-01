"""
Schémas Pydantic pour l'authentification
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from database.models import RoleEnum


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
    nom: str = Field(..., max_length=100, description="Nom de l'utilisateur")
    prenom: str = Field(..., max_length=100, description="Prénom de l'utilisateur")
    email: EmailStr = Field(..., description="Email unique de l'utilisateur")
    telephone: Optional[str] = Field(None, max_length=20, description="Numéro de téléphone")
    password: str = Field(..., min_length=6, description="Mot de passe (minimum 6 caractères)")
    role: str = Field(default="agent_back_office", description="Rôle de l'utilisateur (sera créé automatiquement s'il n'existe pas)")
    
    @validator('role')
    def validate_role(cls, v):
        """Valide le format du rôle (accepte n'importe quelle chaîne, sera créé automatiquement)"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Le rôle ne peut pas être vide")
        # Nettoyer le rôle (enlever espaces, convertir en minuscules)
        return v.strip().lower().replace(' ', '_')


class UserUpdate(BaseModel):
    nom: Optional[str] = Field(None, max_length=100)
    prenom: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    telephone: Optional[str] = Field(None, max_length=20)
    role: Optional[str] = None
    actif: Optional[bool] = None
    
    @validator('role')
    def validate_role(cls, v):
        """Valide que le rôle est valide si fourni"""
        if v is not None:
            valid_roles = [role.value for role in RoleEnum]
            if v not in valid_roles:
                raise ValueError(f"Le rôle doit être l'un des suivants: {', '.join(valid_roles)}")
        return v


class UserChangePassword(BaseModel):
    current_password: str = Field(..., description="Mot de passe actuel")
    new_password: str = Field(..., min_length=6, description="Nouveau mot de passe (minimum 6 caractères)")


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


class UserListResponse(BaseModel):
    """Réponse pour la liste des utilisateurs avec pagination"""
    total: int
    items: List[UserResponse]
    skip: int
    limit: int

