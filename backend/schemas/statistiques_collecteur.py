"""
Schéma Pydantic pour les statistiques d'un collecteur utilisées par l'app mobile
"""

from decimal import Decimal
from pydantic import BaseModel


class StatistiquesCollecteurResponse(BaseModel):
    collecteur_id: int
    total_collecte: Decimal
    commission_totale: Decimal
    nombre_collectes: int
    collectes_completes: int
    collectes_en_attente: int

    class Config:
        from_attributes = True

