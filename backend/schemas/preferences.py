"""
Schémas Pydantic pour la gestion des préférences et accessibilité
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class PreferencesDefaultsResponse(BaseModel):
    theme_defaut: str
    mode_sombre_disponible: bool
    contrastes_disponibles: List[str]
    tailles_police: List[str]
    animations_autorisees: bool
    sons_confirmation: bool


class PreferencesUpdateRequest(BaseModel):
    theme: Optional[str] = Field(None, description="systeme|clair|sombre")
    contraste: Optional[str] = Field(None, description="normal|eleve")
    taille_police: Optional[str] = Field(None, description="petit|moyen|grand")
    animations: Optional[bool] = None
    sons: Optional[bool] = None
    lang: Optional[str] = Field(None, description="Code langue ISO, ex: fr")


class PreferencesUpdateResponse(BaseModel):
    user_id: Optional[int] = None
    collecteur_id: Optional[int] = None
    theme: str
    contraste: str
    taille_police: str
    animations: bool
    sons: bool
    lang: str

    class Config:
        from_attributes = True

