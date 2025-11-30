"""
Schémas Pydantic pour les opérations de caisse
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal
from schemas.collecteur import CollecteurBase


class OperationCaisseBase(BaseModel):
    collecteur_id: int
    type_operation: str = Field(..., description="Type d'opération: entree, sortie, ajustement")
    montant: Decimal = Field(..., gt=0, description="Montant de l'opération")
    libelle: str = Field(..., max_length=200, description="Description de l'opération")
    collecte_id: Optional[int] = None
    reference: Optional[str] = Field(None, max_length=50, description="Référence unique")
    notes: Optional[str] = None
    date_operation: Optional[datetime] = None


class OperationCaisseCreate(OperationCaisseBase):
    pass


class OperationCaisseUpdate(BaseModel):
    libelle: Optional[str] = None
    notes: Optional[str] = None


class OperationCaisseResponse(OperationCaisseBase):
    id: int
    collecteur: Optional[CollecteurBase] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SoldeCaisseResponse(BaseModel):
    """Solde de caisse d'un collecteur"""
    collecteur_id: int
    collecteur_nom: str
    solde_actuel: Decimal
    total_entrees: Decimal
    total_sorties: Decimal
    nombre_operations: int
    derniere_operation: Optional[datetime] = None


class OperationsCaisseListResponse(BaseModel):
    """Réponse avec pagination pour la liste des opérations"""
    items: list[OperationCaisseResponse]
    total: int
    skip: int
    limit: int
    solde_actuel: Decimal

