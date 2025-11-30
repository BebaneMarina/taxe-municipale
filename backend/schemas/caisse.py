"""
Schémas Pydantic pour les caisses des collecteurs
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from schemas.collecteur import CollecteurBase


class CaisseBase(BaseModel):
    collecteur_id: int
    type_caisse: str = Field(..., description="Type de caisse: 'physique' ou 'en_ligne'")
    code: str = Field(..., max_length=50, description="Code unique de la caisse")
    nom: Optional[str] = Field(None, max_length=100)
    solde_initial: Decimal = Field(default=0.00)
    notes: Optional[str] = None
    actif: bool = True


class CaisseCreate(CaisseBase):
    pass


class CaisseUpdate(BaseModel):
    nom: Optional[str] = None
    solde_initial: Optional[Decimal] = None
    etat: Optional[str] = None
    notes: Optional[str] = None
    actif: Optional[bool] = None
    collecteur_id: Optional[int] = None


class CaisseResponse(CaisseBase):
    id: int
    etat: str
    solde_actuel: Decimal
    date_ouverture: Optional[datetime] = None
    date_fermeture: Optional[datetime] = None
    date_cloture: Optional[datetime] = None
    montant_cloture: Optional[Decimal] = None
    collecteur: Optional[CollecteurBase] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OperationCaisseBase(BaseModel):
    caisse_id: int
    type_operation: str = Field(..., description="Type: 'ouverture', 'fermeture', 'entree', 'sortie', 'ajustement', 'cloture'")
    montant: Decimal = Field(..., ge=0, description="Montant de l'opération")
    libelle: str = Field(..., max_length=200)
    collecte_id: Optional[int] = None
    reference: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None


class OperationCaisseCreate(OperationCaisseBase):
    pass


class OperationCaisseResponse(OperationCaisseBase):
    id: int
    collecteur_id: int
    solde_avant: Optional[Decimal] = None
    solde_apres: Optional[Decimal] = None
    date_operation: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EtatCaisseResponse(BaseModel):
    """État détaillé d'une caisse avec statistiques"""
    caisse: CaisseResponse
    nombre_operations: int
    total_entrees: Decimal
    total_sorties: Decimal
    solde_theorique: Decimal
    operations_recentes: List[OperationCaisseResponse] = []


class CaissesListResponse(BaseModel):
    """Réponse avec pagination pour la liste des caisses"""
    items: List[CaisseResponse]
    total: int
    skip: int
    limit: int

