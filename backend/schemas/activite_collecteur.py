"""
Schémas Pydantic pour les activités des collecteurs
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from decimal import Decimal


class ActiviteJour(BaseModel):
    """Activité d'un collecteur pour un jour donné"""
    date: str  # Format YYYY-MM-DD
    nombre_collectes: int
    montant_total: Decimal
    premiere_collecte: Optional[datetime] = None
    derniere_collecte: Optional[datetime] = None
    duree_travail_minutes: Optional[int] = None  # Durée entre première et dernière collecte


class ActiviteCollecteurResponse(BaseModel):
    """Réponse avec les activités d'un collecteur"""
    collecteur_id: int
    collecteur_nom: str
    collecteur_prenom: str
    collecteur_matricule: str
    periode_debut: Optional[str] = None  # Format YYYY-MM-DD
    periode_fin: Optional[str] = None  # Format YYYY-MM-DD
    activites: List[ActiviteJour]
    total_collectes: int
    total_montant: Decimal
    nombre_jours_actifs: int
    moyenne_collectes_par_jour: Optional[float] = None
    moyenne_montant_par_jour: Optional[Decimal] = None

    class Config:
        from_attributes = True

