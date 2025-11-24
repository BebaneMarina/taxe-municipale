"""
Service pour l'intégration avec l'API BambooPay
"""

import os
import base64
import httpx
import logging
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class BambooPayService:
    """Service pour interagir avec l'API BambooPay"""
    
    def __init__(self):
        self.base_url = os.getenv("BAMBOOPAY_BASE_URL", "https://client.bamboopay-ga.com/api")
        self.merchant_id = os.getenv("BAMBOOPAY_MERCHANT_ID", "")
        self.merchant_secret = os.getenv("BAMBOOPAY_MERCHANT_SECRET", "")
        self.debug_mode = os.getenv("BAMBOOPAY_DEBUG", "false").lower() == "true"
        
        if not self.merchant_id or not self.merchant_secret:
            logger.warning("⚠️ BAMBOOPAY_MERCHANT_ID ou BAMBOOPAY_MERCHANT_SECRET non configurés")
    
    def _get_auth_header(self) -> str:
        """Génère l'en-tête d'authentification Basic"""
        credentials = f"{self.merchant_id}:{self.merchant_secret}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"
    
    def _get_headers(self) -> Dict[str, str]:
        """Retourne les en-têtes HTTP pour les requêtes"""
        return {
            "Content-Type": "application/json",
            "Authorization": self._get_auth_header()
        }
    
    async def initier_paiement(
        self,
        payer_name: str,
        matricule: str,
        billing_id: str,
        transaction_amount: str,
        phone: str,
        raison_sociale: Optional[str] = None,
        return_url: Optional[str] = None,
        update_status_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Initie une transaction de paiement via BambooPay
        
        Args:
            payer_name: Nom du payeur
            matricule: Matricule du payeur
            billing_id: ID facture côté marchand
            transaction_amount: Montant à payer (en string)
            phone: Numéro de téléphone du client
            raison_sociale: Raison sociale (optionnel)
            return_url: URL de redirection finale (optionnel)
            update_status_url: URL callback pour mises à jour (optionnel)
        
        Returns:
            Dict avec redirect_url en cas de succès
        """
        url = f"{self.base_url}/send"
        
        payload = {
            "payerName": payer_name,
            "matricule": matricule,
            "billingId": billing_id,
            "transactionAmount": str(transaction_amount),
            "merchant_id": self.merchant_id,
            "phone": phone
        }
        
        if raison_sociale:
            payload["raisonSociale"] = raison_sociale
        if return_url:
            payload["return_url"] = return_url
        if update_status_url:
            payload["update_status_url"] = update_status_url
        
        if self.debug_mode:
            logger.info(f"🌐 Appel BambooPay /send: {url}")
            logger.debug(f"Payload: {payload}")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if self.debug_mode:
                        logger.info(f"✅ Paiement initié avec succès: {data.get('redirect_url', 'N/A')}")
                    return {
                        "success": True,
                        "redirect_url": data.get("redirect_url"),
                        "data": data
                    }
                else:
                    error_data = {}
                    try:
                        error_data = response.json()
                    except:
                        error_data = {"message": response.text}
                    
                    logger.error(f"❌ Erreur BambooPay /send ({response.status_code}): {error_data}")
                    return {
                        "success": False,
                        "error": error_data.get("message", f"Erreur {response.status_code}"),
                        "code": response.status_code,
                        "data": error_data
                    }
        except httpx.TimeoutException:
            logger.error("⏱️ Timeout lors de l'appel à BambooPay")
            return {
                "success": False,
                "error": "Timeout lors de la connexion à BambooPay",
                "code": 408
            }
        except Exception as e:
            logger.error(f"❌ Exception lors de l'appel BambooPay: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"Erreur lors de l'appel à BambooPay: {str(e)}",
                "code": 500
            }
    
    async def paiement_instantane(
        self,
        phone: str,
        amount: str,
        payer_name: str,
        reference: str,
        callback_url: str,
        operateur: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Effectue un paiement instantané via mobile money
        
        Args:
            phone: Numéro du payeur
            amount: Montant (en string)
            payer_name: Nom du payeur
            reference: Référence marchande
            callback_url: URL callback
            operateur: moov_money ou airtel_money (optionnel)
        
        Returns:
            Dict avec reference_bp et status
        """
        url = f"{self.base_url}/mobile/instant-payment"
        
        payload = {
            "phone": phone,
            "amount": str(amount),
            "payer_name": payer_name,
            "reference": reference,
            "merchant_id": self.merchant_id,
            "callback_url": callback_url
        }
        
        if operateur:
            payload["operateur"] = operateur
        
        if self.debug_mode:
            logger.info(f"🌐 Appel BambooPay /mobile/instant-payment: {url}")
            logger.debug(f"Payload: {payload}")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self._get_headers()
                )
                
                if response.status_code == 202:
                    data = response.json()
                    if self.debug_mode:
                        logger.info(f"✅ Paiement instantané initié: {data.get('reference_bp', 'N/A')}")
                    return {
                        "success": data.get("status", False),
                        "reference_bp": data.get("reference_bp"),
                        "reference": data.get("reference"),
                        "message": data.get("message"),
                        "data": data
                    }
                else:
                    error_data = {}
                    try:
                        error_data = response.json()
                    except:
                        error_data = {"message": response.text}
                    
                    logger.error(f"❌ Erreur BambooPay /mobile/instant-payment ({response.status_code}): {error_data}")
                    return {
                        "success": False,
                        "error": error_data.get("message", f"Erreur {response.status_code}"),
                        "code": response.status_code,
                        "data": error_data
                    }
        except httpx.TimeoutException:
            logger.error("⏱️ Timeout lors de l'appel à BambooPay")
            return {
                "success": False,
                "error": "Timeout lors de la connexion à BambooPay",
                "code": 408
            }
        except Exception as e:
            logger.error(f"❌ Exception lors de l'appel BambooPay: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"Erreur lors de l'appel à BambooPay: {str(e)}",
                "code": 500
            }
    
    async def verifier_statut(self, transaction_id: str) -> Dict[str, Any]:
        """
        Vérifie le statut d'une transaction
        
        Args:
            transaction_id: ID de la transaction BambooPay
        
        Returns:
            Dict avec le statut de la transaction
        """
        url = f"{self.base_url}/check-status/{transaction_id}"
        
        if self.debug_mode:
            logger.info(f"🌐 Appel BambooPay /check-status: {url}")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    data = response.json()
                    transaction = data.get("transaction", {})
                    if self.debug_mode:
                        logger.info(f"✅ Statut transaction {transaction_id}: {transaction.get('status', 'N/A')}")
                    return {
                        "success": True,
                        "status": transaction.get("status"),
                        "code": transaction.get("code"),
                        "message": transaction.get("message"),
                        "data": data
                    }
                else:
                    error_data = {}
                    try:
                        error_data = response.json()
                    except:
                        error_data = {"message": response.text}
                    
                    logger.error(f"❌ Erreur BambooPay /check-status ({response.status_code}): {error_data}")
                    return {
                        "success": False,
                        "error": error_data.get("message", f"Erreur {response.status_code}"),
                        "code": response.status_code,
                        "data": error_data
                    }
        except httpx.TimeoutException:
            logger.error("⏱️ Timeout lors de la vérification du statut")
            return {
                "success": False,
                "error": "Timeout lors de la connexion à BambooPay",
                "code": 408
            }
        except Exception as e:
            logger.error(f"❌ Exception lors de la vérification du statut: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"Erreur lors de la vérification: {str(e)}",
                "code": 500
            }


# Instance globale du service
bamboopay_service = BambooPayService()

