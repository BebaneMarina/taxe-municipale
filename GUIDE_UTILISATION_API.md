# Guide d'utilisation de l'API pour développeur mobile

Guide pratique pour utiliser l'API dans votre application mobile.

## Table des matières

1. [Connexion à l'API](#connexion)
2. [Authentification](#authentification)
3. [Utilisation des endpoints](#endpoints)
4. [Exemples de code](#exemples)
5. [Gestion des erreurs](#erreurs)
6. [Bonnes pratiques](#bonnes-pratiques)

---

## Connexion à l'API

### URL de base

```
https://taxe-municipale.onrender.com
```

### Documentation interactive

- **Swagger UI** : https://taxe-municipale.onrender.com/docs
- **ReDoc** : https://taxe-municipale.onrender.com/redoc

### Note importante

Le service gratuit Render se met en veille après 15 minutes d'inactivité. Le premier démarrage après veille peut prendre 30-60 secondes. C'est normal, attendez simplement.

---

## Authentification

### Étape 1 : Obtenir un token

Tous les endpoints (sauf `/api/auth/login`) nécessitent un token JWT.

#### Requête de connexion

```http
POST https://taxe-municipale.onrender.com/api/auth/login
Content-Type: application/x-www-form-urlencoded

username=votre_email@example.com
password=votre_mot_de_passe
```

#### Réponse

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "nom": "Admin",
    "prenom": "Système",
    "email": "admin@example.com",
    "role": "admin"
  }
}
```

### Étape 2 : Utiliser le token

Ajoutez le token dans le header `Authorization` de toutes vos requêtes :

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Durée de validité du token

Le token est valide pendant 24 heures. Après expiration, vous devez vous reconnecter.

---

## Utilisation des endpoints

### 1. Collecteurs

#### Liste des collecteurs

```http
GET https://taxe-municipale.onrender.com/api/collecteurs?actif=true
Authorization: Bearer VOTRE_TOKEN
```

**Paramètres optionnels :**
- `actif` : Filtrer par statut actif (true/false)
- `limit` : Nombre d'éléments (défaut: 100, max: 1000)
- `skip` : Pagination (défaut: 0)
- `search` : Recherche dans nom, prénom, matricule, email

#### Détails d'un collecteur

```http
GET https://taxe-municipale.onrender.com/api/collecteurs/{collecteur_id}
Authorization: Bearer VOTRE_TOKEN
```

### 2. Collectes

#### Liste des collectes

```http
GET https://taxe-municipale.onrender.com/api/collectes?collecteur_id=1&limit=20
Authorization: Bearer VOTRE_TOKEN
```

**Paramètres optionnels :**
- `collecteur_id` : Filtrer par collecteur
- `contribuable_id` : Filtrer par contribuable
- `taxe_id` : Filtrer par taxe
- `statut` : `pending`, `completed`, `failed`, `cancelled`
- `date_debut` : Format `YYYY-MM-DD`
- `date_fin` : Format `YYYY-MM-DD`
- `limit` : Nombre d'éléments
- `skip` : Pagination

#### Créer une collecte

```http
POST https://taxe-municipale.onrender.com/api/collectes
Authorization: Bearer VOTRE_TOKEN
Content-Type: application/json

{
  "contribuable_id": 5,
  "taxe_id": 2,
  "collecteur_id": 1,
  "montant": 10000.00,
  "type_paiement": "especes",
  "billetage": "1x5000, 2x2000, 1x1000",
  "date_collecte": "2024-01-15T14:30:00"
}
```

**Note :** La commission est calculée automatiquement selon le pourcentage de la taxe.

#### Valider une collecte

```http
PATCH https://taxe-municipale.onrender.com/api/collectes/{collecte_id}/valider
Authorization: Bearer VOTRE_TOKEN
```

### 3. Taxes

#### Liste des taxes actives

```http
GET https://taxe-municipale.onrender.com/api/taxes?actif=true&limit=100
Authorization: Bearer VOTRE_TOKEN
```

#### Détails d'une taxe

```http
GET https://taxe-municipale.onrender.com/api/taxes/{taxe_id}
Authorization: Bearer VOTRE_TOKEN
```

### 4. Contribuables

#### Liste des contribuables d'un collecteur

```http
GET https://taxe-municipale.onrender.com/api/contribuables?collecteur_id=1&actif=true
Authorization: Bearer VOTRE_TOKEN
```

### 5. Statistiques

#### Statistiques d'un collecteur

```http
GET https://taxe-municipale.onrender.com/api/rapports/collecteur/{collecteur_id}
Authorization: Bearer VOTRE_TOKEN
```

**Réponse :**
```json
{
  "total_collecte": 500000.00,
  "nombre_collectes": 45,
  "collectes_completes": 40,
  "collectes_en_attente": 5,
  "commission_totale": 25000.00
}
```

---

## Exemples de code

### Flutter/Dart

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  final String baseUrl = 'https://taxe-municipale.onrender.com';
  String? token;
  Map<String, dynamic>? currentUser;

  // Connexion
  Future<bool> login(String email, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/auth/login'),
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: {
          'username': email,
          'password': password,
        },
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        token = data['access_token'];
        currentUser = data['user'];
        return true;
      }
      return false;
    } catch (e) {
      print('Erreur de connexion: $e');
      return false;
    }
  }

  // Liste des collecteurs
  Future<List<dynamic>> getCollecteurs({bool? actif}) async {
    final uri = Uri.parse('$baseUrl/api/collecteurs').replace(
      queryParameters: actif != null ? {'actif': actif.toString()} : null,
    );

    final response = await http.get(
      uri,
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      return json.decode(response.body);
    }
    throw Exception('Erreur: ${response.statusCode}');
  }

  // Liste des collectes
  Future<List<dynamic>> getCollectes({
    int? collecteurId,
    String? statut,
    int limit = 20,
    int skip = 0,
  }) async {
    final queryParams = <String, String>{
      'limit': limit.toString(),
      'skip': skip.toString(),
    };
    
    if (collecteurId != null) {
      queryParams['collecteur_id'] = collecteurId.toString();
    }
    if (statut != null) {
      queryParams['statut'] = statut;
    }

    final uri = Uri.parse('$baseUrl/api/collectes').replace(
      queryParameters: queryParams,
    );

    final response = await http.get(
      uri,
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      return json.decode(response.body);
    }
    throw Exception('Erreur: ${response.statusCode}');
  }

  // Créer une collecte
  Future<Map<String, dynamic>> createCollecte(Map<String, dynamic> data) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/collectes'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
      body: json.encode(data),
    );

    if (response.statusCode == 201) {
      return json.decode(response.body);
    }
    throw Exception('Erreur: ${response.statusCode} - ${response.body}');
  }

  // Valider une collecte
  Future<Map<String, dynamic>> validerCollecte(int collecteId) async {
    final response = await http.patch(
      Uri.parse('$baseUrl/api/collectes/$collecteId/valider'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      return json.decode(response.body);
    }
    throw Exception('Erreur: ${response.statusCode}');
  }

  // Liste des taxes actives
  Future<List<dynamic>> getTaxes() async {
    final response = await http.get(
      Uri.parse('$baseUrl/api/taxes?actif=true&limit=100'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      return json.decode(response.body);
    }
    throw Exception('Erreur: ${response.statusCode}');
  }

  // Statistiques d'un collecteur
  Future<Map<String, dynamic>> getStatistiques(int collecteurId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/api/rapports/collecteur/$collecteurId'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      return json.decode(response.body);
    }
    throw Exception('Erreur: ${response.statusCode}');
  }
}
```

### React Native (JavaScript)

```javascript
const API_BASE_URL = 'https://taxe-municipale.onrender.com';

class ApiService {
  constructor() {
    this.token = null;
    this.currentUser = null;
  }

  // Connexion
  async login(email, password) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `username=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`,
      });

      if (response.ok) {
        const data = await response.json();
        this.token = data.access_token;
        this.currentUser = data.user;
        return true;
      }
      return false;
    } catch (error) {
      console.error('Erreur de connexion:', error);
      return false;
    }
  }

  // Liste des collecteurs
  async getCollecteurs(actif = null) {
    const params = new URLSearchParams();
    if (actif !== null) {
      params.append('actif', actif);
    }

    const response = await fetch(
      `${API_BASE_URL}/api/collecteurs?${params.toString()}`,
      {
        headers: {
          'Authorization': `Bearer ${this.token}`,
          'Content-Type': 'application/json',
        },
      }
    );

    if (response.ok) {
      return await response.json();
    }
    throw new Error(`Erreur: ${response.status}`);
  }

  // Liste des collectes
  async getCollectes({ collecteurId, statut, limit = 20, skip = 0 }) {
    const params = new URLSearchParams({
      limit: limit.toString(),
      skip: skip.toString(),
    });
    
    if (collecteurId) {
      params.append('collecteur_id', collecteurId);
    }
    if (statut) {
      params.append('statut', statut);
    }

    const response = await fetch(
      `${API_BASE_URL}/api/collectes?${params.toString()}`,
      {
        headers: {
          'Authorization': `Bearer ${this.token}`,
          'Content-Type': 'application/json',
        },
      }
    );

    if (response.ok) {
      return await response.json();
    }
    throw new Error(`Erreur: ${response.status}`);
  }

  // Créer une collecte
  async createCollecte(data) {
    const response = await fetch(`${API_BASE_URL}/api/collectes`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (response.ok) {
      return await response.json();
    }
    const error = await response.json();
    throw new Error(`Erreur: ${response.status} - ${error.detail || error.message}`);
  }

  // Valider une collecte
  async validerCollecte(collecteId) {
    const response = await fetch(
      `${API_BASE_URL}/api/collectes/${collecteId}/valider`,
      {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${this.token}`,
          'Content-Type': 'application/json',
        },
      }
    );

    if (response.ok) {
      return await response.json();
    }
    throw new Error(`Erreur: ${response.status}`);
  }

  // Liste des taxes
  async getTaxes() {
    const response = await fetch(
      `${API_BASE_URL}/api/taxes?actif=true&limit=100`,
      {
        headers: {
          'Authorization': `Bearer ${this.token}`,
          'Content-Type': 'application/json',
        },
      }
    );

    if (response.ok) {
      return await response.json();
    }
    throw new Error(`Erreur: ${response.status}`);
  }

  // Statistiques
  async getStatistiques(collecteurId) {
    const response = await fetch(
      `${API_BASE_URL}/api/rapports/collecteur/${collecteurId}`,
      {
        headers: {
          'Authorization': `Bearer ${this.token}`,
          'Content-Type': 'application/json',
        },
      }
    );

    if (response.ok) {
      return await response.json();
    }
    throw new Error(`Erreur: ${response.status}`);
  }
}

export default ApiService;
```

---

## Gestion des erreurs

### Codes de statut HTTP

- `200` : Succès
- `201` : Créé avec succès
- `204` : Supprimé avec succès
- `400` : Requête invalide (vérifiez les données envoyées)
- `401` : Non authentifié (token invalide ou expiré)
- `403` : Accès interdit (permissions insuffisantes)
- `404` : Ressource non trouvée
- `422` : Erreur de validation (données incorrectes)
- `500` : Erreur serveur

### Gestion des erreurs (Flutter)

```dart
Future<void> handleApiCall() async {
  try {
    final data = await apiService.getCollecteurs();
    // Traiter les données
  } on http.ClientException catch (e) {
    // Erreur de connexion réseau
    print('Erreur réseau: $e');
  } catch (e) {
    // Autre erreur
    print('Erreur: $e');
  }
}
```

### Gestion des erreurs (React Native)

```javascript
try {
  const data = await apiService.getCollecteurs();
  // Traiter les données
} catch (error) {
  if (error.message.includes('401')) {
    // Token expiré, reconnecter l'utilisateur
    await apiService.login(email, password);
  } else if (error.message.includes('network')) {
    // Erreur réseau
    console.error('Erreur réseau:', error);
  } else {
    // Autre erreur
    console.error('Erreur:', error);
  }
}
```

### Token expiré

Si vous recevez une erreur `401 Unauthorized`, le token a probablement expiré. Vous devez :

1. Détecter l'erreur 401
2. Demander à l'utilisateur de se reconnecter
3. Obtenir un nouveau token
4. Réessayer la requête

---

## Bonnes pratiques

### 1. Stockage du token

**Flutter :**
```dart
import 'package:shared_preferences/shared_preferences.dart';

// Sauvegarder le token
final prefs = await SharedPreferences.getInstance();
await prefs.setString('token', token);

// Récupérer le token
final token = prefs.getString('token');
```

**React Native :**
```javascript
import AsyncStorage from '@react-native-async-storage/async-storage';

// Sauvegarder le token
await AsyncStorage.setItem('token', token);

// Récupérer le token
const token = await AsyncStorage.getItem('token');
```

### 2. Intercepteur pour ajouter le token automatiquement

**Flutter :**
```dart
class AuthenticatedClient extends http.BaseClient {
  final String token;
  final http.Client _inner;

  AuthenticatedClient(this.token) : _inner = http.Client();

  Future<http.StreamedResponse> send(http.BaseRequest request) {
    request.headers['Authorization'] = 'Bearer $token';
    return _inner.send(request);
  }
}
```

**React Native :**
```javascript
// Utiliser un intercepteur axios ou modifier fetch
const authenticatedFetch = async (url, options = {}) => {
  const token = await AsyncStorage.getItem('token');
  return fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${token}`,
    },
  });
};
```

### 3. Gestion de la pagination

```dart
// Flutter
Future<List<dynamic>> getAllCollectes(int collecteurId) async {
  List<dynamic> allCollectes = [];
  int skip = 0;
  const int limit = 100;
  bool hasMore = true;

  while (hasMore) {
    final collectes = await apiService.getCollectes(
      collecteurId: collecteurId,
      limit: limit,
      skip: skip,
    );

    allCollectes.addAll(collectes);
    
    if (collectes.length < limit) {
      hasMore = false;
    } else {
      skip += limit;
    }
  }

  return allCollectes;
}
```

### 4. Mise en cache

Pour améliorer les performances, mettez en cache les données qui changent peu (taxes, types de contribuables, etc.).

### 5. Gestion du mode hors ligne

Détectez si l'utilisateur est hors ligne et stockez les données localement pour les synchroniser plus tard.

### 6. Timeout des requêtes

Configurez un timeout pour éviter que l'application reste bloquée :

**Flutter :**
```dart
final response = await http.get(uri).timeout(
  Duration(seconds: 10),
  onTimeout: () {
    throw TimeoutException('La requête a pris trop de temps');
  },
);
```

**React Native :**
```javascript
const controller = new AbortController();
const timeoutId = setTimeout(() => controller.abort(), 10000);

const response = await fetch(url, {
  signal: controller.signal,
});
clearTimeout(timeoutId);
```

---

## Workflow recommandé

### 1. Au démarrage de l'application

1. Vérifier si un token est stocké localement
2. Si oui, vérifier qu'il est encore valide (tester avec une requête simple)
3. Si non valide, demander à l'utilisateur de se connecter

### 2. Pendant l'utilisation

1. Charger les données nécessaires (collecteurs, taxes, etc.)
2. Mettre en cache les données statiques
3. Synchroniser les collectes créées localement

### 3. Création d'une collecte

1. Valider les données localement
2. Envoyer à l'API
3. Si succès, mettre à jour l'interface
4. Si erreur, afficher un message et permettre de réessayer

---

## Test de l'API

### Avec Swagger UI

1. Allez sur : https://taxe-municipale.onrender.com/docs
2. Cliquez sur "Authorize" (cadenas) en haut à droite
3. Dans la modal :
   - **username** : Entrez votre email (ex: `admin@example.com`)
   - **password** : Entrez votre mot de passe
   - **client_id** : Laissez vide (pas nécessaire)
   - **client_secret** : Laissez vide (pas nécessaire)
4. Cliquez sur "Authorize"
5. Si les identifiants sont corrects, vous êtes connecté
6. Testez les endpoints directement dans l'interface

**Note :** Voir `GUIDE_AUTHENTIFICATION_SWAGGER.md` pour plus de détails sur l'authentification dans Swagger UI.

### Avec Postman

1. Créez une nouvelle requête
2. URL : `https://taxe-municipale.onrender.com/api/auth/login`
3. Méthode : POST
4. Body : `x-www-form-urlencoded`
5. Entrez `username` et `password`
6. Copiez le token de la réponse
7. Pour les autres requêtes, ajoutez dans Headers : `Authorization: Bearer VOTRE_TOKEN`

---

## Support

- **Documentation complète** : Voir `API_DOCUMENTATION.md`
- **Swagger UI** : https://taxe-municipale.onrender.com/docs
- **En cas de problème** : Contactez l'administrateur de l'API

