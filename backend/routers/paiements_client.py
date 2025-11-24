"""
Routes pour le paiement client via BambooPay
Interface publique pour les clients
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from database.database import get_db
from database.models import Taxe, TransactionBambooPay, StatutTransactionEnum, AffectationTaxe, Contribuable
from schemas.transaction import TransactionCreate, TransactionResponse, TransactionStatusResponse, CallbackData
from services.bamboopay import bamboopay_service
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/client", tags=["paiements-client"])


@router.get("/taxes", response_model=List[dict])
def get_taxes_publiques(
    actif: bool = Query(True, description="Uniquement les taxes actives"),
    db: Session = Depends(get_db)
):
    """
    Récupère la liste des taxes disponibles pour le paiement public
    """
    query = db.query(Taxe).filter(Taxe.actif == actif)
    taxes = query.all()
    
    return [
        {
            "id": taxe.id,
            "nom": taxe.nom,
            "description": taxe.description,
            "montant": float(taxe.montant),
            "periodicite": taxe.periodicite,
            "service": taxe.service.nom if taxe.service else None
        }
        for taxe in taxes
    ]


@router.post("/paiement/initier", response_model=TransactionResponse)
async def initier_paiement(
    transaction: TransactionCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Initie un paiement via BambooPay
    """
    # Vérifier que la taxe existe
    taxe = db.query(Taxe).filter(Taxe.id == transaction.taxe_id, Taxe.actif == True).first()
    if not taxe:
        raise HTTPException(status_code=404, detail="Taxe non trouvée ou inactive")
    
    # Générer un billing_id unique
    billing_id = f"TAX-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
    
    # Construire les URLs de callback
    base_url = str(request.base_url).rstrip('/')
    return_url = f"{base_url}/client/paiement/retour"
    callback_url = f"{base_url}/api/client/paiement/callback"
    
    # Créer la transaction en base
    db_transaction = TransactionBambooPay(
        contribuable_id=transaction.contribuable_id,
        affectation_taxe_id=transaction.affectation_taxe_id,
        taxe_id=transaction.taxe_id,
        payer_name=transaction.payer_name,
        phone=transaction.phone,
        matricule=transaction.matricule,
        raison_sociale=transaction.raison_sociale,
        billing_id=billing_id,
        transaction_amount=taxe.montant,
        return_url=return_url,
        callback_url=callback_url,
        payment_method=transaction.payment_method,
        operateur=transaction.operateur,
        statut=StatutTransactionEnum.PENDING
    )
    db.add(db_transaction)
    db.commit()
    # Ne pas utiliser db.refresh() pour éviter les problèmes de colonnes manquantes
    # db.refresh(db_transaction)
    
    # Initier le paiement selon la méthode
    if transaction.payment_method == "mobile_instant":
        # Paiement instantané mobile
        result = await bamboopay_service.paiement_instantane(
            phone=transaction.phone,
            amount=str(taxe.montant),
            payer_name=transaction.payer_name,
            reference=billing_id,
            callback_url=callback_url,
            operateur=transaction.operateur
        )
        
        if result.get("success"):
            db_transaction.reference_bp = result.get("reference_bp")
            db_transaction.statut = StatutTransactionEnum.PENDING
            db.commit()
            
            return TransactionResponse(
                id=db_transaction.id,
                billing_id=billing_id,
                transaction_amount=taxe.montant,
                statut="pending",
                reference_bp=result.get("reference_bp"),
                message="Paiement instantané initié. Vérifiez votre téléphone."
            )
        else:
            db_transaction.statut = StatutTransactionEnum.FAILED
            db_transaction.statut_message = result.get("error", "Erreur inconnue")
            db.commit()
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Erreur lors de l'initiation du paiement")
            )
    else:
        # Paiement web (redirection)
        result = await bamboopay_service.initier_paiement(
            payer_name=transaction.payer_name,
            matricule=transaction.matricule or "",
            billing_id=billing_id,
            transaction_amount=str(taxe.montant),
            phone=transaction.phone,
            raison_sociale=transaction.raison_sociale,
            return_url=return_url,
            update_status_url=callback_url
        )
        
        if result.get("success"):
            redirect_url = result.get("redirect_url")
            if redirect_url:
                return TransactionResponse(
                    id=db_transaction.id,
                    billing_id=billing_id,
                    transaction_amount=taxe.montant,
                    statut="pending",
                    redirect_url=redirect_url,
                    message="Redirection vers BambooPay..."
                )
            else:
                raise HTTPException(status_code=500, detail="URL de redirection non reçue")
        else:
            db_transaction.statut = StatutTransactionEnum.FAILED
            db_transaction.statut_message = result.get("error", "Erreur inconnue")
            db.commit()
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Erreur lors de l'initiation du paiement")
            )


@router.post("/paiement/callback")
async def callback_bamboopay(
    callback_data: CallbackData,
    db: Session = Depends(get_db)
):
    """
    Endpoint de callback appelé par BambooPay pour mettre à jour le statut d'une transaction
    """
    logger.info(f"📞 Callback BambooPay reçu: {callback_data.dict()}")
    
    # Trouver la transaction par billing_id ou reference_bp
    transaction = None
    if callback_data.billing_id:
        transaction = db.query(TransactionBambooPay).filter(
            TransactionBambooPay.billing_id == callback_data.billing_id
        ).first()
    elif callback_data.reference_bp:
        transaction = db.query(TransactionBambooPay).filter(
            TransactionBambooPay.reference_bp == callback_data.reference_bp
        ).first()
    elif callback_data.transaction_id:
        transaction = db.query(TransactionBambooPay).filter(
            TransactionBambooPay.transaction_id == callback_data.transaction_id
        ).first()
    
    if not transaction:
        logger.warning(f"⚠️ Transaction non trouvée pour callback: {callback_data.dict()}")
        return JSONResponse(
            status_code=404,
            content={"message": "Transaction non trouvée"}
        )
    
    # Mettre à jour le statut
    statut_bp = callback_data.statut or ""
    if statut_bp.lower() in ["success", "completed", "paid"]:
        transaction.statut = StatutTransactionEnum.SUCCESS
        transaction.date_paiement = datetime.utcnow()
        
        # Créer une collecte si nécessaire
        if transaction.taxe_id and transaction.contribuable_id:
            from database.models import InfoCollecte, StatutCollecteEnum, TypePaiementEnum
            from database.models import Collecteur
            
            # Trouver un collecteur système ou le premier disponible
            collecteur = db.query(Collecteur).filter(Collecteur.actif == True).first()
            if collecteur:
                # Vérifier si une collecte existe déjà
                existing_collecte = db.query(InfoCollecte).filter(
                    InfoCollecte.contribuable_id == transaction.contribuable_id,
                    InfoCollecte.taxe_id == transaction.taxe_id,
                    func.date(InfoCollecte.date_collecte) == datetime.utcnow().date()
                ).first()
                
                if not existing_collecte:
                    collecte = InfoCollecte(
                        contribuable_id=transaction.contribuable_id,
                        taxe_id=transaction.taxe_id,
                        collecteur_id=collecteur.id,
                        montant=transaction.transaction_amount,
                        type_paiement=TypePaiementEnum.MOBILE_MONEY,
                        statut=StatutCollecteEnum.COMPLETED,
                        reference=f"BP-{transaction.billing_id}",
                        date_collecte=datetime.utcnow()
                    )
                    db.add(collecte)
    elif statut_bp.lower() in ["failed", "error"]:
        transaction.statut = StatutTransactionEnum.FAILED
    elif statut_bp.lower() in ["cancelled", "canceled"]:
        transaction.statut = StatutTransactionEnum.CANCELLED
    
    transaction.transaction_id = callback_data.transaction_id or transaction.transaction_id
    transaction.reference_bp = callback_data.reference_bp or transaction.reference_bp
    transaction.statut_message = callback_data.message
    transaction.date_callback = datetime.utcnow()
    transaction.updated_at = datetime.utcnow()
    
    db.commit()
    
    logger.info(f"✅ Transaction {transaction.billing_id} mise à jour: {transaction.statut}")
    
    return JSONResponse(
        status_code=200,
        content={"message": "Callback traité avec succès"}
    )


@router.get("/paiement/statut/{billing_id}", response_model=TransactionStatusResponse)
def get_statut_transaction(
    billing_id: str,
    db: Session = Depends(get_db)
):
    """
    Récupère le statut d'une transaction
    """
    transaction = db.query(TransactionBambooPay).filter(
        TransactionBambooPay.billing_id == billing_id
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction non trouvée")
    
    return TransactionStatusResponse(
        id=transaction.id,
        billing_id=transaction.billing_id,
        reference_bp=transaction.reference_bp,
        transaction_id=transaction.transaction_id,
        statut=transaction.statut.value,
        statut_message=transaction.statut_message,
        transaction_amount=transaction.transaction_amount,
        date_initiation=transaction.date_initiation,
        date_paiement=transaction.date_paiement
    )


@router.post("/paiement/verifier/{billing_id}")
async def verifier_statut_bamboopay(
    billing_id: str,
    db: Session = Depends(get_db)
):
    """
    Vérifie le statut d'une transaction directement auprès de BambooPay
    """
    transaction = db.query(TransactionBambooPay).filter(
        TransactionBambooPay.billing_id == billing_id
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction non trouvée")
    
    if not transaction.reference_bp and not transaction.transaction_id:
        raise HTTPException(status_code=400, detail="Aucune référence BambooPay disponible")
    
    # Vérifier le statut auprès de BambooPay
    transaction_id = transaction.transaction_id or transaction.reference_bp
    result = await bamboopay_service.verifier_statut(transaction_id)
    
    if result.get("success"):
        # Mettre à jour le statut local
        statut_bp = result.get("status", "").lower()
        if statut_bp in ["success", "completed", "paid"]:
            transaction.statut = StatutTransactionEnum.SUCCESS
            if not transaction.date_paiement:
                transaction.date_paiement = datetime.utcnow()
        elif statut_bp in ["failed", "error"]:
            transaction.statut = StatutTransactionEnum.FAILED
        elif statut_bp in ["cancelled", "canceled"]:
            transaction.statut = StatutTransactionEnum.CANCELLED
        
        transaction.statut_message = result.get("message")
        transaction.updated_at = datetime.utcnow()
        db.commit()
    
    return {
        "billing_id": billing_id,
        "statut_local": transaction.statut.value,
        "statut_bamboopay": result.get("status"),
        "message": result.get("message")
    }

