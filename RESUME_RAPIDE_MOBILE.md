# Résumé rapide : Utiliser l'API dans l'app mobile

## URL de l'API

```
https://taxe-municipale.onrender.com
```

## Les 3 étapes essentielles

### 1. Connexion

```javascript
// Envoyer email et mot de passe
POST https://taxe-municipale.onrender.com/api/auth/login
Content-Type: application/x-www-form-urlencoded

username=email@example.com
password=mot_de_passe
```

**Réponse :** Vous recevez un `access_token` → **STOCKEZ-LE !**

### 2. Utiliser le token

Pour TOUTES les autres requêtes, ajoutez dans les headers :

```
Authorization: Bearer VOTRE_TOKEN
```

### 3. Les endpoints principaux

#### Liste des collectes d'un collecteur
```
GET /api/collectes?collecteur_id=1
Authorization: Bearer VOTRE_TOKEN
```

#### Créer une collecte
```
POST /api/collectes
Authorization: Bearer VOTRE_TOKEN
Content-Type: application/json

{
  "contribuable_id": 5,
  "taxe_id": 2,
  "collecteur_id": 1,
  "montant": 10000.00,
  "type_paiement": "especes"
}
```

#### Liste des taxes
```
GET /api/taxes?actif=true
Authorization: Bearer VOTRE_TOKEN
```

#### Statistiques
```
GET /api/rapports/collecteur/1
Authorization: Bearer VOTRE_TOKEN
```

## Code minimal (Flutter)

```dart
// 1. Connexion
final response = await http.post(
  Uri.parse('https://taxe-municipale.onrender.com/api/auth/login'),
  headers: {'Content-Type': 'application/x-www-form-urlencoded'},
  body: {'username': email, 'password': password},
);
final token = json.decode(response.body)['access_token'];

// 2. Utiliser le token
final collectes = await http.get(
  Uri.parse('https://taxe-municipale.onrender.com/api/collectes?collecteur_id=1'),
  headers: {'Authorization': 'Bearer $token'},
);
```

## Code minimal (React Native)

```javascript
// 1. Connexion
const response = await fetch('https://taxe-municipale.onrender.com/api/auth/login', {
  method: 'POST',
  headers: {'Content-Type': 'application/x-www-form-urlencoded'},
  body: `username=${email}&password=${password}`,
});
const { access_token } = await response.json();

// 2. Utiliser le token
const collectes = await fetch('https://taxe-municipale.onrender.com/api/collectes?collecteur_id=1', {
  headers: {'Authorization': `Bearer ${access_token}`},
});
```

## Points importants

1. **Stocker le token** après connexion (SharedPreferences/AsyncStorage)
2. **Ajouter le token** dans toutes les requêtes protégées
3. **Gérer l'erreur 401** (token expiré) → reconnecter l'utilisateur
4. **Timeout** : Le service peut être en veille (attendre 30-60 secondes la première fois)

## Documentation complète

- **Guide pratique** : `GUIDE_PRATIQUE_MOBILE.md` (exemples complets)
- **Documentation API** : `API_DOCUMENTATION.md` (tous les endpoints)
- **Swagger UI** : https://taxe-municipale.onrender.com/docs

