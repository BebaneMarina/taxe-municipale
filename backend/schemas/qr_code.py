"""
Schémas Pydantic pour les endpoints QR Code
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal


class ContribuableQRResponse(BaseModel):
    """Réponse pour un contribuable récupéré par QR code"""
    id: int
    nom: str
    prenom: Optional[str] = None
    telephone: str
    email: Optional[str] = None
    adresse: Optional[str] = None
    nom_activite: Optional[str] = None
    numero_identification: Optional[str] = None
    qr_code: Optional[str] = None
    actif: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CollecteQRResponse(BaseModel):
    """Réponse pour une collecte vérifiée par QR code"""
    id: int
    reference: str
    montant: Decimal
    commission: Decimal
    type_paiement: str
    statut: str
    date_collecte: datetime
    contribuable: Optional[Dict[str, Any]] = None
    taxe: Optional[Dict[str, Any]] = None
    collecteur: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True

