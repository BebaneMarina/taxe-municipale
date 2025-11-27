"""
Schémas Pydantic pour les journaux de travaux et les commissions
"""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel


class JournalTravauxBase(BaseModel):
    date_jour: date
    statut: str
    nb_collectes: int
    montant_collectes: Decimal
    nb_operations_caisse: int
    total_entrees_caisse: Decimal
    total_sorties_caisse: Decimal
    relances_envoyees: int
    impayes_regles: int
    remarque: Optional[str] = None


class JournalTravauxResponse(JournalTravauxBase):
    id: int
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None
    closed_by: Optional[int] = None

    class Config:
        from_attributes = True


class JournalComputedResponse(JournalTravauxBase):
    caisses_ouvertes: int
    toutes_caisses_fermees: bool


class ClotureRequest(BaseModel):
    remarque: Optional[str] = None


class CommissionItem(BaseModel):
    collecteur_id: int
    collecteur_nom: Optional[str] = None
    montant_collecte: Decimal
    commission_montant: Decimal
    commission_pourcentage: Decimal
    statut_paiement: str


class CommissionFichierResponse(BaseModel):
    id: int
    date_jour: date
    chemin: str
    type_fichier: str
    statut: str
    created_at: datetime
    file_metadata: Optional[dict] = None

    class Config:
        from_attributes = True


class CommissionGenerationResponse(BaseModel):
    fichier: CommissionFichierResponse
    commissions: List[CommissionItem]


class CommissionJournalResponse(BaseModel):
    id: int
    date_jour: date
    collecteur_id: int
    collecteur_nom: Optional[str] = None
    collecteur_matricule: Optional[str] = None
    montant_collecte: Decimal
    commission_montant: Decimal
    commission_pourcentage: Decimal
    statut_paiement: str
    fichier_id: Optional[int] = None
    created_at: datetime

