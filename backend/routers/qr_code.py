"""
Routes pour la gestion des QR codes
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import Contribuable, InfoCollecte
from schemas.qr_code import ContribuableQRResponse, CollecteQRResponse
from auth.security import get_current_active_user
from typing import Dict, Any
import json

router = APIRouter(
    prefix="/api",
    tags=["qr_code"],
    dependencies=[Depends(get_current_active_user)],
)


@router.get("/contribuables/qr/{qr_code}", response_model=ContribuableQRResponse)
def get_contribuable_by_qr(
    qr_code: str,
    db: Session = Depends(get_db),
):
    """
    Récupérer un contribuable par son QR code
    """
    contribuable = db.query(Contribuable).filter(
        Contribuable.qr_code == qr_code,
        Contribuable.actif == True  # noqa: E712
    ).first()
    
    if not contribuable:
        raise HTTPException(status_code=404, detail="Contribuable non trouvé pour ce QR code")
    
    return contribuable


@router.get("/collectes/qr/{qr_code}", response_model=CollecteQRResponse)
def verify_receipt_qr(
    qr_code: str,
    db: Session = Depends(get_db),
):
    """
    Vérifier un reçu par QR code
    Le QR code contient un JSON encodé avec la structure:
    {
        "type": "receipt",
        "collecte_id": 123,
        "reference": "REF-2024-001",
        "timestamp": "2024-01-15T10:30:00Z"
    }
    """
    try:
        # Décoder le QR code (JSON)
        qr_data = json.loads(qr_code)
        
        if qr_data.get("type") != "receipt":
            raise HTTPException(status_code=400, detail="QR code invalide")
        
        collecte_id = qr_data.get("collecte_id")
        reference = qr_data.get("reference")
        
        if not collecte_id or not reference:
            raise HTTPException(status_code=400, detail="QR code incomplet")
        
        # Récupérer la collecte
        from database.models import StatutCollecteEnum
        collecte = db.query(InfoCollecte).filter(
            InfoCollecte.id == collecte_id,
            InfoCollecte.reference == reference,
            InfoCollecte.statut == StatutCollecteEnum.COMPLETED
        ).first()
        
        if not collecte:
            raise HTTPException(status_code=404, detail="Reçu non trouvé pour ce QR code")
        
        # Construire la réponse avec les relations
        response_data: Dict[str, Any] = {
            "id": collecte.id,
            "reference": collecte.reference,
            "montant": collecte.montant,
            "commission": collecte.commission,
            "type_paiement": collecte.type_paiement.value if hasattr(collecte.type_paiement, 'value') else str(collecte.type_paiement),
            "statut": collecte.statut.value if hasattr(collecte.statut, 'value') else str(collecte.statut),
            "date_collecte": collecte.date_collecte,
            "created_at": collecte.created_at,
        }
        
        # Ajouter les relations si disponibles
        if collecte.contribuable:
            response_data["contribuable"] = {
                "id": collecte.contribuable.id,
                "nom": collecte.contribuable.nom,
                "prenom": collecte.contribuable.prenom,
                "telephone": collecte.contribuable.telephone
            }
        
        if collecte.taxe:
            response_data["taxe"] = {
                "id": collecte.taxe.id,
                "nom": collecte.taxe.nom,
                "code": collecte.taxe.code,
                "montant": float(collecte.taxe.montant)
            }
        
        if collecte.collecteur:
            response_data["collecteur"] = {
                "id": collecte.collecteur.id,
                "nom": collecte.collecteur.nom,
                "prenom": collecte.collecteur.prenom,
                "matricule": collecte.collecteur.matricule
            }
        
        return response_data
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Format de QR code invalide")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la vérification: {str(e)}")

