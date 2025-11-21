"""
Schémas Pydantic pour les types de contribuables
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TypeContribuableBase(BaseModel):
    nom: str = Field(..., max_length=50)
    code: str = Field(..., max_length=20)
    description: Optional[str] = None
    actif: bool = True


class TypeContribuableCreate(TypeContribuableBase):
    pass


class TypeContribuableResponse(TypeContribuableBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

