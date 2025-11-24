"""
Schémas Pydantic pour la localisation et les traductions
"""

from typing import Dict, List
from pydantic import BaseModel


class TexteLocalisationResponse(BaseModel):
    lang: str
    version: int
    strings: Dict[str, str]


class LangueDisponibleItem(BaseModel):
    code: str
    nom: str
    direction: str
    defaut: bool
    version: int


class LanguesDisponiblesResponse(BaseModel):
    langues: List[LangueDisponibleItem]

