# Intégration API Ventis Messaging pour les Relances Automatiques

## Vue d'ensemble

L'API Ventis Messaging a été intégrée dans le système de relances pour permettre l'envoi automatique de SMS aux contribuables en retard de paiement.

## Configuration

### 1. Variables d'environnement

Ajoutez ces variables dans votre fichier `.env` du backend :

```env
# Configuration API Ventis Messaging
VENTIS_MESSAGING_URL=https://messaging.ventis.group/messaging/api/v1
KEYCLOAK_MESSAGING_HOST=https://signin.ventis.group
KEYCLOAK_MESSAGING_REALM=Messaging
KEYCLOAK_MESSAGING_CLIENT_ID=api-messaging
KEYCLOAK_MESSAGING_CLIENT_SECRET=votre-client-secret
KEYCLOAK_MESSAGING_USERNAME=test-send-sms
KEYCLOAK_MESSAGING_PASSWORD=votre-mot-de-passe
KEYCLOAK_VERIFY_SSL=false
VENTIS_DEBUG=false
```

### 2. Installation des dépendances

```bash
cd backend
pip install httpx==0.27.0
```

Ou réinstallez toutes les dépendances :
```bash
pip install -r requirements.txt
```

## Fonctionnalités

### 1. Envoi manuel d'une relance

L'endpoint `PATCH /api/relances/{relance_id}/envoyer` :
- Envoie automatiquement le SMS si le type est `sms` et que le contribuable a un téléphone
- Met à jour le statut de la relance (`envoyee` ou `echec`)
- Enregistre l'UUID du message dans les notes pour traçabilité

**Exemple :**
```bash
PATCH /api/relances/1/envoyer
```

### 2. Génération automatique avec envoi

L'endpoint `POST /api/relances/generer-automatique` accepte le paramètre `envoyer_automatiquement` :

**Génération seule (sans envoi) :**
```bash
POST /api/relances/generer-automatique?jours_retard_min=7&type_relance=sms&limite=50&envoyer_automatiquement=false
```

**Génération + Envoi automatique :**
```bash
POST /api/relances/generer-automatique?jours_retard_min=7&type_relance=sms&limite=50&envoyer_automatiquement=true
```

### 3. Interface utilisateur

Dans la page "Relances" :
- Bouton "Générer relances automatiques"
- Deux confirmations :
  1. Confirmation de génération
  2. Choix d'envoi automatique ou manuel
- Affichage des statistiques (envoyées, échecs, en attente)

## Format des numéros de téléphone

Le service formate automatiquement les numéros au format Ventis (241XXXXXXXX) :
- `0661234567` → `2410661234567`
- `+2410661234567` → `2410661234567`
- `2410661234567` → `2410661234567`

## Gestion des erreurs

- **Succès** : Statut `envoyee`, UUID stocké dans les notes
- **Échec** : Statut `echec`, message d'erreur dans les notes
- **Token expiré** : Renouvellement automatique du token Keycloak
- **Timeout** : Erreur 408, relance marquée comme échec

## Logs

Les logs sont enregistrés via le module `logging` de Python :
- Mode debug : `VENTIS_DEBUG=true`
- Logs d'envoi, erreurs, et renouvellement de tokens

## Structure des fichiers

- `backend/services/ventis_messaging.py` : Service d'intégration Ventis
- `backend/routers/relances.py` : Endpoints modifiés pour l'envoi automatique
- `e_taxe_back_office/src/app/components/pages/relances/` : Interface utilisateur

## Test

1. Configurez les variables d'environnement
2. Redémarrez le serveur FastAPI
3. Accédez à la page "Relances"
4. Cliquez sur "Générer relances automatiques"
5. Choisissez d'envoyer automatiquement ou non
6. Vérifiez les statuts des relances dans le tableau

## Dépannage

### Erreur "Impossible de récupérer le token"
- Vérifiez les credentials Keycloak dans `.env`
- Vérifiez la connexion à `KEYCLOAK_MESSAGING_HOST`

### Erreur "ENDPOINT_NOT_FOUND"
- Vérifiez `VENTIS_MESSAGING_URL`
- Contactez le support Ventis pour confirmer l'URL

### SMS non envoyés
- Vérifiez que les contribuables ont un numéro de téléphone valide
- Vérifiez les logs avec `VENTIS_DEBUG=true`
- Vérifiez le statut des relances (échec = voir les notes)

