"""
Schémas Pydantic pour les transactions BambooPay
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class TransactionCreate(BaseModel):
    """Schéma pour créer une transaction"""
    taxe_id: int
    payer_name: str = Field(..., max_length=200)
    phone: str = Field(..., max_length=20)
    matricule: Optional[str] = Field(None, max_length=50)
    raison_sociale: Optional[str] = Field(None, max_length=200)
    contribuable_id: Optional[int] = None
    affectation_taxe_id: Optional[int] = None
    payment_method: str = Field(default="web", description="web ou mobile_instant")
    operateur: Optional[str] = Field(None, description="moov_money ou airtel_money pour paiement instantané")


class TransactionResponse(BaseModel):
    """Réponse avec les informations de transaction"""
    id: int
    billing_id: str
    transaction_amount: Decimal
    statut: str
    redirect_url: Optional[str] = None
    reference_bp: Optional[str] = None
    message: Optional[str] = None

    class Config:
        from_attributes = True


class TransactionStatusResponse(BaseModel):
    """Réponse pour le statut d'une transaction"""
    id: int
    billing_id: str
    reference_bp: Optional[str] = None
    transaction_id: Optional[str] = None
    statut: str
    statut_message: Optional[str] = None
    transaction_amount: Decimal
    date_initiation: datetime
    date_paiement: Optional[datetime] = None

    class Config:
        from_attributes = True


class CallbackData(BaseModel):
    """Données reçues du callback BambooPay"""
    transaction_id: Optional[str] = None
    reference_bp: Optional[str] = None
    billing_id: Optional[str] = None
    statut: Optional[str] = None
    message: Optional[str] = None
    amount: Optional[str] = None

