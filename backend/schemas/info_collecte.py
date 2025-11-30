"""
Schémas Pydantic pour les collectes
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from decimal import Decimal
from schemas.contribuable import ContribuableBase
from schemas.taxe import TaxeBase
from schemas.collecteur import CollecteurBase


class InfoCollecteBase(BaseModel):
    contribuable_id: int
    taxe_id: int
    collecteur_id: int
    montant: Decimal = Field(..., ge=0)
    type_paiement: str  # "especes", "mobile_money", "carte"
    billetage: Optional[str] = None  # JSON string
    date_collecte: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("type_paiement", mode="before")
    @classmethod
    def normalize_type_paiement(cls, value: str) -> str:
        """
        Convertit les variantes saisies côté mobile en valeurs supportées par l'enum.
        - "cash", "especes", "espece" -> "especes"
        - "bamboo", "bamboopay" -> "mobile_money"
        - "mobile", "mobile_money" -> "mobile_money"
        - "card", "carte" -> "carte"
        """
        if not value:
            return "especes"

        normalized = value.strip().lower()
        mapping = {
            "cash": "especes",
            "espece": "especes",
            "especes": "especes",
            "mobile": "mobile_money",
            "mobile_money": "mobile_money",
            "mobile-money": "mobile_money",
            "bamboo": "mobile_money",
            "bamboopay": "mobile_money",
            "carte": "carte",
            "card": "carte",
            "visa": "carte",
            "mastercard": "carte",
        }
        allowed = {"especes", "mobile_money", "carte"}
        mapped = mapping.get(normalized, normalized)
        return mapped if mapped in allowed else "especes"


class InfoCollecteCreate(InfoCollecteBase):
    pass


class InfoCollecteUpdate(BaseModel):
    statut: Optional[str] = None  # "pending", "completed", "failed", "cancelled"
    annule: Optional[bool] = None
    raison_annulation: Optional[str] = None
    sms_envoye: Optional[bool] = None
    ticket_imprime: Optional[bool] = None


class LocationInfo(BaseModel):
    """Informations de géolocalisation d'une collecte"""
    id: int
    latitude: Decimal
    longitude: Decimal
    accuracy: Optional[Decimal] = None
    timestamp: Optional[datetime] = None

    class Config:
        from_attributes = True


class InfoCollecteResponse(InfoCollecteBase):
    id: int
    commission: Decimal
    statut: str
    reference: str
    date_cloture: Optional[datetime] = None
    sms_envoye: bool
    ticket_imprime: bool
    annule: bool
    raison_annulation: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    contribuable: Optional[ContribuableBase] = None
    taxe: Optional[TaxeBase] = None
    collecteur: Optional[CollecteurBase] = None
    location: Optional[LocationInfo] = None

    class Config:
        from_attributes = True

    # Filet de sécurité pour éviter les null côté mobile (Flutter)
    @field_validator("reference", mode="after")
    def default_reference(cls, value: Optional[str], info):
        """
        Garantit une référence non nulle pour éviter les cast null -> String côté Flutter.
        """
        if value:
            return value
        collecte_id = info.data.get("id")
        return f"COL-{collecte_id}" if collecte_id is not None else ""

    @field_validator("type_paiement", mode="after")
    def default_type_paiement(cls, value: Optional[str]):
        """
        Garantit un type de paiement non nul.
        """
        return value or "especes"

    @field_validator("billetage", "raison_annulation", mode="after")
    def default_empty_string(cls, value: Optional[str]):
        """
        Convertit les champs textuels optionnels en chaîne vide plutôt que null.
        """
        return value or ""

