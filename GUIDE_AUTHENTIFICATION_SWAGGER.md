# Guide : Authentification dans Swagger UI

## À quoi sert cette modal ?

Cette modal d'authentification dans Swagger UI permet de :
1. **Se connecter** à l'API pour obtenir un token JWT
2. **Tester les endpoints protégés** directement dans l'interface Swagger
3. **Éviter de copier-coller le token** à chaque requête

## Pourquoi l'erreur 401 ?

L'erreur 401 apparaît parce que :
- Vous n'avez pas encore entré vos identifiants
- Ou les identifiants sont incorrects
- Ou le formulaire n'est pas correctement rempli

## Comment utiliser cette modal correctement

### Méthode 1 : Utilisation simple (Recommandée)

Votre API utilise une authentification simple avec **username** et **password** uniquement.

**Étapes :**

1. **Cliquez sur le bouton "Authorize"** (cadenas) en haut à droite de Swagger UI

2. **Dans la modal qui s'ouvre :**
   - **username** : Entrez votre email (ex: `admin@example.com`)
   - **password** : Entrez votre mot de passe
   - **client_id** : Laissez vide (pas nécessaire)
   - **client_secret** : Laissez vide (pas nécessaire)

3. **Cliquez sur "Authorize"**

4. Si les identifiants sont corrects, vous verrez un message de succès et la modal se fermera

5. **Maintenant, tous les endpoints protégés** utiliseront automatiquement votre token

### Méthode 2 : Authentification manuelle

Si la modal ne fonctionne pas, vous pouvez :

1. **Obtenir le token manuellement** :
   - Utilisez l'endpoint `/api/auth/login` dans Swagger
   - Entrez votre email et mot de passe
   - Copiez le `access_token` de la réponse

2. **Ajouter le token manuellement** :
   - Cliquez sur "Authorize"
   - Dans le champ qui apparaît, entrez : `Bearer VOTRE_TOKEN`
   - Cliquez sur "Authorize"

## Détails techniques

### Configuration de l'API

Votre API utilise :
- **OAuth2PasswordBearer** : C'est le schéma d'authentification FastAPI
- **Token URL** : `/api/auth/login`
- **Flow** : `password` (OAuth2 password flow)

### Ce qui est nécessaire

- ✅ **username** : Votre email
- ✅ **password** : Votre mot de passe
- ❌ **client_id** : Pas nécessaire (laissez vide)
- ❌ **client_secret** : Pas nécessaire (laissez vide)

### Ce qui se passe en arrière-plan

1. Swagger envoie vos identifiants à `/api/auth/login`
2. L'API vérifie les identifiants
3. Si correct, l'API retourne un token JWT
4. Swagger stocke ce token
5. Pour chaque requête protégée, Swagger ajoute automatiquement : `Authorization: Bearer VOTRE_TOKEN`

## Résolution des problèmes

### Erreur 401 : "response status is 401"

**Causes possibles :**
1. Email ou mot de passe incorrect
2. Compte utilisateur désactivé
3. Format des identifiants incorrect

**Solutions :**
1. Vérifiez que vous utilisez le bon email (pas le nom d'utilisateur)
2. Vérifiez votre mot de passe
3. Assurez-vous que votre compte est actif
4. Essayez de vous connecter directement via l'endpoint `/api/auth/login` pour voir le message d'erreur exact

### La modal demande client_id et client_secret

**Solution :** Laissez ces champs **vides**. Votre API n'en a pas besoin.

### Le token expire

**Solution :** 
- Les tokens sont valides pendant 30 jours
- Si le token expire, reconnectez-vous via "Authorize"
- Swagger vous demandera automatiquement de vous reconnecter si le token est expiré

### Les requêtes retournent toujours 401

**Vérifications :**
1. Avez-vous cliqué sur "Authorize" et entré vos identifiants ?
2. Le token est-il bien stocké ? (vérifiez qu'il y a un cadenas fermé à côté de "Authorize")
3. Essayez de vous déconnecter et reconnecter

## Exemple d'utilisation

### Étape 1 : Se connecter

1. Ouvrez Swagger UI : `https://taxe-municipale.onrender.com/docs`
2. Cliquez sur **"Authorize"** (cadenas en haut à droite)
3. Entrez :
   - **username** : `admin@example.com`
   - **password** : `votre_mot_de_passe`
4. Cliquez sur **"Authorize"**

### Étape 2 : Tester un endpoint

1. Trouvez un endpoint protégé (ex: `GET /api/collecteurs`)
2. Cliquez sur **"Try it out"**
3. Cliquez sur **"Execute"**
4. La requête devrait fonctionner avec votre token automatiquement

### Étape 3 : Vérifier le token

Pour voir le token utilisé :
1. Cliquez à nouveau sur **"Authorize"**
2. Vous verrez le token stocké (masqué par des points)
3. Vous pouvez le copier si nécessaire

## Alternative : Utiliser l'endpoint directement

Si la modal ne fonctionne pas, vous pouvez :

1. **Utiliser l'endpoint `/api/auth/login`** :
   - Cliquez sur l'endpoint
   - Cliquez sur "Try it out"
   - Entrez votre email et mot de passe
   - Cliquez sur "Execute"
   - Copiez le `access_token` de la réponse

2. **Ajouter le token manuellement** :
   - Cliquez sur "Authorize"
   - Dans le champ, entrez : `Bearer VOTRE_TOKEN_COPIE`
   - Cliquez sur "Authorize"

## Bonnes pratiques

1. **Ne partagez jamais votre token** : Il donne accès à votre compte
2. **Déconnectez-vous** après utilisation (cliquez sur "Authorize" puis "Logout")
3. **Utilisez des comptes de test** pour le développement
4. **Vérifiez les permissions** : Certains endpoints nécessitent des rôles spécifiques (admin, collecteur, etc.)

## Support

Si vous continuez à avoir des problèmes :
1. Vérifiez que l'API est accessible : `https://taxe-municipale.onrender.com/health`
2. Vérifiez vos identifiants avec l'endpoint `/api/auth/login` directement
3. Consultez les logs dans Render Dashboard pour voir les erreurs serveur

