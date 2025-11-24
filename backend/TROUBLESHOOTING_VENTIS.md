# Dépannage API Ventis Messaging

## Erreur : "Client secret not provided in request" (401)

### Problème
Keycloak exige le `client_secret` pour authentifier votre client, mais il n'est pas configuré.

### Solution

1. **Vérifiez votre configuration Keycloak** :
   - Connectez-vous à l'interface d'administration Keycloak
   - Allez dans le realm "Messaging"
   - Vérifiez le client "api-messaging"
   - Regardez si "Client authentication" est activé (ON)

2. **Si "Client authentication" est ON** :
   - Vous DEVEZ fournir le `client_secret`
   - Récupérez le secret depuis Keycloak (onglet "Credentials")
   - Ajoutez-le dans votre `.env` :
   ```env
   KEYCLOAK_MESSAGING_CLIENT_SECRET=votre-client-secret-ici
   ```

3. **Si "Client authentication" est OFF** :
   - Le `client_secret` n'est pas requis
   - Mais l'erreur peut venir d'une autre configuration
   - Vérifiez que le client est configuré pour accepter le grant type "password"

### Vérification rapide

Vérifiez que votre `.env` contient bien :
```env
KEYCLOAK_MESSAGING_CLIENT_SECRET=votre-secret-ici
```

**Important** : Ne mettez PAS d'espaces autour du `=` et ne mettez PAS de guillemets autour de la valeur.

## Erreur : "Impossible de récupérer le token d'accès"

### Causes possibles

1. **Credentials incorrects** :
   - Vérifiez `KEYCLOAK_MESSAGING_USERNAME`
   - Vérifiez `KEYCLOAK_MESSAGING_PASSWORD`
   - Vérifiez `KEYCLOAK_MESSAGING_CLIENT_ID`

2. **URL Keycloak incorrecte** :
   - Vérifiez `KEYCLOAK_MESSAGING_HOST`
   - Vérifiez `KEYCLOAK_MESSAGING_REALM`
   - Testez l'URL dans un navigateur : `https://signin.ventis.group/realms/Messaging`

3. **Client non configuré correctement** :
   - Le client doit avoir le grant type "password" activé
   - Le client doit être "public" ou avoir un secret configuré

## Test de connexion

Pour tester votre configuration, vous pouvez créer un script de test :

```python
import asyncio
from services.ventis_messaging import ventis_messaging_service

async def test():
    token = await ventis_messaging_service.get_access_token()
    if token:
        print("✅ Token récupéré avec succès")
    else:
        print("❌ Impossible de récupérer le token")
        print("Vérifiez vos credentials dans le fichier .env")

asyncio.run(test())
```

## Erreur 500 lors de l'envoi

Si vous obtenez une erreur 500, vérifiez :
1. Les logs du serveur pour voir l'erreur exacte
2. Que le token a bien été récupéré
3. Que le numéro de téléphone est au bon format
4. Que l'URL de l'API Ventis est correcte

## Mode debug

Activez le mode debug pour voir plus de détails :
```env
VENTIS_DEBUG=true
```

Cela affichera dans les logs :
- Les URLs utilisées
- Les requêtes envoyées
- Les réponses reçues
- Les erreurs détaillées

