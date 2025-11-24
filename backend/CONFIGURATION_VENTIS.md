# Configuration API Ventis Messaging

## Variables d'environnement requises

Ajoutez ces variables dans votre fichier `.env` :

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

## Installation

1. Installer la dépendance `httpx` :
```bash
pip install httpx==0.27.0
```

Ou ajoutez-la à `requirements.txt` et réinstallez :
```bash
pip install -r requirements.txt
```

## Utilisation

### Envoi manuel d'une relance

L'endpoint `/api/relances/{relance_id}/envoyer` envoie automatiquement le SMS si :
- Le type de relance est `sms`
- Le contribuable a un numéro de téléphone

### Génération automatique avec envoi

L'endpoint `/api/relances/generer-automatique` accepte maintenant le paramètre `envoyer_automatiquement` :

```bash
POST /api/relances/generer-automatique?jours_retard_min=7&type_relance=sms&limite=50&envoyer_automatiquement=true
```

Si `envoyer_automatiquement=true`, les SMS seront envoyés immédiatement après la génération des relances.

## Format des numéros de téléphone

Le service formate automatiquement les numéros au format attendu par Ventis (241XXXXXXXX) :
- `0661234567` → `2410661234567`
- `+2410661234567` → `2410661234567`
- `2410661234567` → `2410661234567`

## Gestion des erreurs

- Les erreurs d'envoi sont enregistrées dans le champ `notes` de la relance
- Le statut de la relance est mis à `echec` en cas d'erreur
- Le statut est mis à `envoyee` en cas de succès
- L'UUID du message est stocké dans les notes pour traçabilité

## Logs

Les logs sont enregistrés via le module `logging` de Python. Activez le mode debug avec :
```env
VENTIS_DEBUG=true
```

