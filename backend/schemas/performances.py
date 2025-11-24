"""
Schémas Pydantic pour le suivi des performances des collecteurs
"""

from typing import List, Optional
from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime


class ObjectifsCollecteurResponse(BaseModel):
    collecteur_id: int
    objectif_journalier: Decimal
    objectif_hebdo: Decimal
    objectif_mensuel: Decimal
    devise: str
    periode_courante: str

    class Config:
        from_attributes = True


class PerformancePoint(BaseModel):
    label: str
    date_debut: datetime
    date_fin: datetime
    montant: Decimal
    nombre_collectes: int

    class Config:
        from_attributes = True


class PerformancesResponse(BaseModel):
    periode: str
    points: List[PerformancePoint]
    progression_vs_objectif: Decimal


class BadgeItem(BaseModel):
    code: str
    label: str
    description: Optional[str]
    statut: str
    date_obtention: Optional[datetime]

    class Config:
        from_attributes = True


class BadgesResponse(BaseModel):
    badges: List[BadgeItem]


class FeedbackRequest(BaseModel):
    badge_code: str
    feedback: Optional[str] = None

