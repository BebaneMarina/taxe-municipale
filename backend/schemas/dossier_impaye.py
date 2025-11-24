"""
Schémas Pydantic pour les dossiers d'impayés
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from schemas.contribuable import ContribuableBase
from schemas.affectation_taxe import AffectationTaxeBase
from schemas.collecteur import CollecteurBase


class DossierImpayeBase(BaseModel):
    contribuable_id: int
    affectation_taxe_id: int
    montant_initial: Decimal
    date_echeance: datetime
    notes: Optional[str] = None


class DossierImpayeCreate(DossierImpayeBase):
    pass


class DossierImpayeUpdate(BaseModel):
    montant_paye: Optional[Decimal] = None
    penalites: Optional[Decimal] = None
    statut: Optional[str] = None
    priorite: Optional[str] = None
    dernier_contact: Optional[datetime] = None
    notes: Optional[str] = None
    assigne_a: Optional[int] = None
    date_assignation: Optional[datetime] = None
    date_cloture: Optional[datetime] = None


class DossierImpayeResponse(DossierImpayeBase):
    id: int
    montant_paye: Decimal
    montant_restant: Decimal
    penalites: Decimal
    jours_retard: int
    statut: str
    priorite: str
    dernier_contact: Optional[datetime] = None
    nombre_relances: int
    assigne_a: Optional[int] = None
    date_assignation: Optional[datetime] = None
    date_cloture: Optional[datetime] = None
    contribuable: Optional[ContribuableBase] = None
    affectation_taxe: Optional[AffectationTaxeBase] = None
    collecteur: Optional[CollecteurBase] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DossierImpayeListResponse(BaseModel):
    items: List[DossierImpayeResponse]
    total: int
    skip: int
    limit: int


class CalculPenalitesRequest(BaseModel):
    montant_initial: Decimal
    date_echeance: datetime
    taux_penalite_journalier: Optional[Decimal] = Field(default=Decimal("0.5"), description="Taux de pénalité par jour en %")
    jours_retard: Optional[int] = None  # Si None, calcule depuis date_echeance jusqu'à aujourd'hui


class CalculPenalitesResponse(BaseModel):
    montant_initial: Decimal
    jours_retard: int
    taux_penalite_journalier: Decimal
    penalites_calculees: Decimal
    montant_total: Decimal

