"""
Service pour interagir avec l'API externe Ventis Messaging
Intégration pour l'envoi automatique de SMS dans le système de relances
"""

import httpx
import asyncio
from typing import Dict, Any, Optional
import os
from datetime import datetime
import time
import logging

logger = logging.getLogger(__name__)


class VentisMessagingService:
    """Service pour interagir avec l'API externe Ventis Messaging"""

    def __init__(self):
        # Configuration depuis .env
        self.base_url = os.getenv("VENTIS_MESSAGING_URL", "https://messaging.ventis.group/messaging/api/v1")
        
        # Alternative endpoints à tester si le principal ne fonctionne pas
        self.alternative_endpoints = [
            "/message",
            "/messages", 
            "/sms",
            "/send"
        ]
        
        # Configuration Keycloak
        self.keycloak_host = os.getenv("KEYCLOAK_MESSAGING_HOST", "https://signin.ventis.group")
        self.keycloak_realm = os.getenv("KEYCLOAK_MESSAGING_REALM", "Messaging")
        self.client_id = os.getenv("KEYCLOAK_MESSAGING_CLIENT_ID", "api-messaging")
        client_secret_env = os.getenv("KEYCLOAK_MESSAGING_CLIENT_SECRET", "")
        self.client_secret = client_secret_env.strip() if client_secret_env else ""
        self.username = os.getenv("KEYCLOAK_MESSAGING_USERNAME", "test-send-sms")
        self.password = os.getenv("KEYCLOAK_MESSAGING_PASSWORD", "12345678")
        
        # Avertir si le client_secret n'est pas configuré
        if not self.client_secret:
            logger.warning("⚠️ KEYCLOAK_MESSAGING_CLIENT_SECRET n'est pas configuré dans le fichier .env")
            logger.warning("   Cela peut causer des erreurs d'authentification si Keycloak l'exige.")
            logger.warning("   Ajoutez KEYCLOAK_MESSAGING_CLIENT_SECRET=votre-secret dans votre fichier .env")
        
        # Default sender id autorisé par Ventis
        self.default_sender = os.getenv("VENTIS_MESSAGING_SENDER", "VENTIS")

        # Avertir si le client_secret n'est pas configuré (peut être requis selon la config Keycloak)
        if not self.client_secret:
            logger.warning("KEYCLOAK_MESSAGING_CLIENT_SECRET n'est pas configuré. Cela peut causer des erreurs d'authentification si requis par Keycloak.")
        self.verify_ssl = os.getenv("KEYCLOAK_VERIFY_SSL", "false").lower() == "true"
        
        # Token d'accès (sera récupéré dynamiquement)
        self.access_token: Optional[str] = None
        self.token_expiry: Optional[float] = None
        
        # Mode debug
        self.debug_mode = os.getenv("VENTIS_DEBUG", "false").lower() == "true"
        
        logger.info(f"VentisMessagingService initialisé - API URL: {self.base_url}")

    async def get_access_token(self, force_refresh: bool = False) -> Optional[str]:
        """
        Récupère un token d'accès OAuth2 depuis Keycloak
        Utilise le grant type 'password' (Resource Owner Password Credentials)
        """
        # Si le token existe et n'est pas expiré, le retourner
        if not force_refresh and self.access_token and self.token_expiry and time.time() < self.token_expiry:
            if self.debug_mode:
                remaining_time = int(self.token_expiry - time.time())
                logger.debug(f"Utilisation du token existant (expire dans {remaining_time}s)")
            return self.access_token

        logger.info("Récupération d'un nouveau token d'accès Keycloak...")
        
        # Invalider le token actuel
        self.access_token = None
        self.token_expiry = None
        
        # Construire l'URL du token endpoint
        token_url = f"{self.keycloak_host}/realms/{self.keycloak_realm}/protocol/openid-connect/token"
        
        # Préparer les données de la requête
        data = {
            "grant_type": "password",
            "client_id": self.client_id,
            "username": self.username,
            "password": self.password
        }
        
        # Ajouter le client_secret seulement s'il est défini et non vide
        if self.client_secret and self.client_secret.strip():
            data["client_secret"] = self.client_secret.strip()
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        try:
            async with httpx.AsyncClient(verify=self.verify_ssl) as client:
                response = await client.post(
                    token_url,
                    data=data,
                    headers=headers,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    token_data = response.json()
                    self.access_token = token_data["access_token"]
                    
                    # Calculer l'expiration (90% de la durée de vie du token)
                    expires_in = token_data.get("expires_in", 300)
                    self.token_expiry = time.time() + (expires_in * 0.9)
                    
                    logger.info(f"Token récupéré avec succès (expire dans {expires_in}s)")
                    return self.access_token
                elif response.status_code == 401:
                    error_data = {}
                    try:
                        if response.headers.get("content-type", "").startswith("application/json"):
                            error_data = response.json()
                    except:
                        pass
                    error_desc = error_data.get("error_description", response.text)
                    logger.error(f"Erreur authentification Keycloak (401): {error_desc}")
                    
                    # Si c'est un problème de client_secret, donner un message plus clair
                    if "client secret" in error_desc.lower():
                        logger.error("❌ Le client_secret est requis mais n'est pas configuré")
                        logger.error("   Vérifiez votre fichier .env et ajoutez KEYCLOAK_MESSAGING_CLIENT_SECRET")
                        logger.error("   Ou contactez l'administrateur Keycloak pour obtenir le secret")
                    return None
                else:
                    logger.error(f"Erreur récupération token: {response.status_code} - {response.text}")
                    return None
                    
        except httpx.ConnectError as e:
            logger.error(f"Erreur de connexion à Keycloak: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Exception lors de la récupération du token: {str(e)}")
            return None

    def parse_ventis_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse la réponse de l'API Ventis au format pipe-delimited
        Format attendu: +SUCCESS|uuid|timestamp OU -ERROR|error_code|error_message
        """
        response_text = response_text.strip()
        
        # Initialiser la structure de base
        result = {
            'raw': response_text,
            'parsed': False
        }
        
        # Vérifier si la réponse contient des pipes
        if '|' in response_text:
            parts = response_text.split('|')
            
            # Cas de succès: +SUCCESS|uuid|timestamp
            if len(parts) >= 3 and parts[0].upper() in ['+SUCCESS', 'SUCCESS']:
                result.update({
                    'parsed': True,
                    'status': 'SUCCESS',
                    'uuid': parts[1].strip(),
                    'timestamp': parts[2].strip() if len(parts) > 2 else None
                })
            
            # Cas d'erreur: -ERROR|error_code|error_message
            elif len(parts) >= 2 and parts[0].upper() in ['-ERROR', 'ERROR']:
                result.update({
                    'parsed': True,
                    'status': 'ERROR',
                    'error_code': parts[1].strip() if len(parts) > 1 else 'UNKNOWN',
                    'error_message': parts[2].strip() if len(parts) > 2 else 'Unknown error'
                })
        
        return result

    async def try_send_with_endpoint(
        self,
        endpoint: str,
        payload: Dict[str, Any],
        headers: Dict[str, str],
        retry_on_auth_error: bool = True
    ) -> tuple[bool, Dict[str, Any]]:
        """Tente d'envoyer un message via un endpoint spécifique"""
        try:
            async with httpx.AsyncClient(verify=self.verify_ssl) as client:
                response = await client.post(
                    endpoint,
                    json=payload,
                    headers=headers,
                    timeout=30.0
                )
                
                if self.debug_mode:
                    logger.debug(f"Essai endpoint: {endpoint} - Status: {response.status_code}")
                
                # GESTION AUTOMATIQUE DE L'EXPIRATION DU TOKEN
                if response.status_code == 401 and retry_on_auth_error:
                    logger.warning("Erreur 401 - Token expiré, récupération d'un nouveau token...")
                    
                    # Forcer le refresh du token
                    new_token = await self.get_access_token(force_refresh=True)
                    
                    if new_token:
                        # Mettre à jour le header avec le nouveau token
                        headers['Authorization'] = f'Bearer {new_token}'
                        
                        # Réessayer la requête avec le nouveau token
                        logger.info("Nouvelle tentative avec le nouveau token...")
                        return await self.try_send_with_endpoint(
                            endpoint,
                            payload,
                            headers,
                            retry_on_auth_error=False
                        )
                    else:
                        return False, {
                            'status_code': 401,
                            'detail': 'Impossible de récupérer un nouveau token après expiration'
                        }
                
                if response.status_code == 200:
                    response_data = self.parse_ventis_response(response.text)
                    
                    if response_data.get('parsed') and response_data.get('status') == 'SUCCESS':
                        return True, {
                            'success': True,
                            'status_code': 200,
                            'data': response_data,
                            'endpoint_used': endpoint,
                            'detail': 'Message envoyé avec succès'
                        }
                
                # Si ce n'est pas un succès, continuer
                return False, {
                    'status_code': response.status_code,
                    'detail': response.text
                }
                
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi: {str(e)}")
            return False, {
                'error': str(e)
            }

    async def send_message(
        self, 
        to: str, 
        message: str, 
        sender: Optional[str] = None,
        is_otp: bool = False
    ) -> Dict[str, Any]:
        """
        Envoie un message SMS via l'API Ventis
        
        Args:
            to: Numéro du destinataire (format: 241XXXXXXXX)
            message: Contenu du message
            sender: Nom de l'expéditeur
            is_otp: True si c'est un OTP, False sinon
            
        Returns:
            Dict contenant le résultat de l'envoi
        """
        try:
            logger.info(f"Envoi SMS via Ventis - Destinataire: {to}, Sender: {sender}")
            
            # Récupérer le token d'accès
            access_token = await self.get_access_token()
            if not access_token:
                logger.error("Impossible de récupérer le token d'accès")
                return {
                    'success': False,
                    'status_code': 401,
                    'error': 'AUTH_ERROR',
                    'detail': 'Impossible de récupérer le token d\'accès Keycloak'
                }
            
            # Préparer les headers
            headers = {
                'Content-Type': 'application/json; charset=UTF-8',
                'Connection': 'keep-alive',
                'Authorization': f'Bearer {access_token}'
            }
            
            # Payload conforme à la documentation Ventis
            sender_value = sender or self.default_sender

            payload = {
                "to": to,
                "sender": sender_value,
                "isOTP": is_otp,
                "message": message
            }
            
            # Essayer l'endpoint principal
            main_endpoint = f"{self.base_url}/message"
            
            success, result = await self.try_send_with_endpoint(
                main_endpoint,
                payload,
                headers
            )
            
            if success:
                logger.info(f"SMS envoyé avec succès via {result['endpoint_used']}")
                return result
            
            # Si l'endpoint principal échoue avec 404, essayer les alternatives
            if result.get('status_code') == 404:
                logger.warning("Endpoint principal introuvable (404), essai des alternatives...")
                
                for alt_path in self.alternative_endpoints:
                    if alt_path == "/message":  # Déjà testé
                        continue
                    
                    alt_endpoint = f"{self.base_url.rsplit('/', 1)[0]}{alt_path}"
                    
                    success, result = await self.try_send_with_endpoint(
                        alt_endpoint,
                        payload,
                        headers
                    )
                    
                    if success:
                        logger.info(f"SMS envoyé avec succès via endpoint alternatif: {result['endpoint_used']}")
                        return result
                
                # Aucun endpoint n'a fonctionné
                logger.error("Aucun endpoint API Ventis trouvé")
                return {
                    'success': False,
                    'status_code': 404,
                    'error': 'ENDPOINT_NOT_FOUND',
                    'detail': 'Aucun endpoint API valide trouvé. Vérifiez la documentation Ventis.'
                }
            
            # Autre erreur que 404
            logger.error(f"Erreur API Ventis: {result.get('status_code')}")
            return {
                'success': False,
                'status_code': result.get('status_code', 500),
                'error': f"API_ERROR_{result.get('status_code', 500)}",
                'detail': result.get('detail', 'Erreur inconnue')
            }
                    
        except httpx.TimeoutException:
            logger.error("Timeout de la requête vers l'API Ventis")
            return {
                'success': False,
                'status_code': 408,
                'error': 'TIMEOUT',
                'detail': 'La requête a expiré (timeout 30s)'
            }
        except httpx.ConnectError as e:
            logger.error(f"Erreur de connexion à l'API Ventis: {str(e)}")
            return {
                'success': False,
                'status_code': 503,
                'error': 'CONNECTION_ERROR',
                'detail': f'Impossible de se connecter à l\'API Ventis: {str(e)}'
            }
        except Exception as e:
            logger.error(f"Erreur inattendue lors de l'envoi SMS: {str(e)}")
            return {
                'success': False,
                'status_code': 500,
                'error': 'UNEXPECTED_ERROR',
                'detail': str(e)
            }

    def format_phone_number(self, phone: str) -> str:
        """
        Formate un numéro de téléphone au format attendu par Ventis (241XXXXXXXX)
        
        Args:
            phone: Numéro de téléphone dans n'importe quel format
            
        Returns:
            Numéro formaté (241XXXXXXXX)
        """
        # Supprimer tous les caractères non numériques
        cleaned = ''.join(filter(str.isdigit, phone))
        
        # Si le numéro commence par 241, le retourner tel quel
        if cleaned.startswith('241'):
            return cleaned
        
        # Si le numéro commence par 0, remplacer par 241
        if cleaned.startswith('0'):
            return '241' + cleaned[1:]
        
        # Si le numéro commence par +241, supprimer le +
        if cleaned.startswith('241'):
            return cleaned
        
        # Sinon, ajouter 241 au début
        return '241' + cleaned


# Instance globale du service
ventis_messaging_service = VentisMessagingService()

