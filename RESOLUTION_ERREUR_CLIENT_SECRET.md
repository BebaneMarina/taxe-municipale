# Résolution de l'erreur "Client secret not provided"

## Problème

Vous obtenez l'erreur :
```
Erreur récupération token: 401 - {"error":"unauthorized_client","error_description":"Client secret not provided in request"}
```

## Cause

Keycloak exige le `client_secret` pour authentifier votre client, mais cette variable n'est pas configurée dans votre fichier `.env`.

## Solution

### Option 1 : Ajouter le client_secret (Recommandé)

1. **Récupérez le client_secret depuis Keycloak** :
   - Connectez-vous à l'interface d'administration Keycloak
   - Allez dans le realm "Messaging"
   - Cliquez sur "Clients" → "api-messaging"
   - Allez dans l'onglet "Credentials"
   - Copiez le "Client Secret"

2. **Ajoutez-le dans votre fichier `.env`** :
   ```env
   KEYCLOAK_MESSAGING_CLIENT_SECRET=votre-client-secret-ici
   ```

3. **Redémarrez le serveur FastAPI**

### Option 2 : Configurer Keycloak pour ne pas exiger le secret

Si vous avez accès à l'administration Keycloak, vous pouvez :

1. Aller dans le client "api-messaging"
2. Désactiver "Client authentication" (le mettre sur OFF)
3. OU configurer le client comme "Public client"

**Note** : Cette option dépend de votre politique de sécurité. Contactez l'administrateur Keycloak si nécessaire.

## Vérification

Après avoir ajouté le `client_secret`, vérifiez les logs au démarrage du serveur. Vous devriez voir :
- ✅ "Token récupéré avec succès" au lieu de l'erreur 401

## Fichier .env complet

Votre fichier `.env` devrait contenir au minimum :

```env
# Configuration API Ventis Messaging
VENTIS_MESSAGING_URL=https://messaging.ventis.group/messaging/api/v1
KEYCLOAK_MESSAGING_HOST=https://signin.ventis.group
KEYCLOAK_MESSAGING_REALM=Messaging
KEYCLOAK_MESSAGING_CLIENT_ID=api-messaging
KEYCLOAK_MESSAGING_CLIENT_SECRET=votre-secret-ici
KEYCLOAK_MESSAGING_USERNAME=test-send-sms
KEYCLOAK_MESSAGING_PASSWORD=votre-mot-de-passe
KEYCLOAK_VERIFY_SSL=false
VENTIS_DEBUG=false
```

## Important

- Ne mettez PAS d'espaces autour du `=` dans le `.env`
- Ne mettez PAS de guillemets autour des valeurs
- Le `client_secret` est sensible - ne le partagez pas publiquement

