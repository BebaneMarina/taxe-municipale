# 📚 Documentation API - Application Mobile

Documentation complète des endpoints pour l'application mobile.

## 🔗 URL de base

**Production (Render) :** `https://votre-app.onrender.com`  
**Développement :** `http://localhost:8000`

## 🔐 Authentification

Tous les endpoints (sauf `/api/auth/login`) nécessitent un token JWT dans le header :

```
Authorization: Bearer VOTRE_TOKEN
```

### Obtenir un token

```http
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=votre_email@example.com
password=votre_mot_de_passe
```

**Réponse :**
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

---

## 📋 COLLECTEURS

### 1. Liste des collecteurs

```http
GET /api/collecteurs
```

**Paramètres de requête (optionnels) :**
- `skip` (int) : Nombre d'éléments à sauter (défaut: 0)
- `limit` (int) : Nombre d'éléments à retourner (défaut: 100, max: 1000)
- `actif` (bool) : Filtrer par statut actif
- `statut` (string) : `active` ou `desactive`
- `etat` (string) : `connecte` ou `deconnecte`
- `search` (string) : Recherche dans nom, prénom, matricule, email

**Exemple :**
```http
GET /api/collecteurs?actif=true&limit=50
```

**Réponse :**
```json
[
  {
    "id": 1,
    "nom": "Dupont",
    "prenom": "Jean",
    "matricule": "COL-001",
    "email": "jean.dupont@example.com",
    "telephone": "+241 066 12 34 56",
    "statut": "active",
    "etat": "deconnecte",
    "actif": true,
    "zone_id": 1,
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00"
  }
]
```

### 2. Détails d'un collecteur

```http
GET /api/collecteurs/{collecteur_id}
```

**Réponse :** Même format que la liste

### 3. Créer un collecteur

```http
POST /api/collecteurs
Content-Type: application/json
```

**Body :**
```json
{
  "nom": "Dupont",
  "prenom": "Jean",
  "matricule": "COL-001",
  "email": "jean.dupont@example.com",
  "telephone": "+241 066 12 34 56",
  "zone_id": 1,
  "actif": true
}
```

**Réponse :** 201 Created avec l'objet créé

### 4. Modifier un collecteur

```http
PUT /api/collecteurs/{collecteur_id}
Content-Type: application/json
```

**Body :** Mêmes champs que la création (tous optionnels)

### 5. Supprimer un collecteur

```http
DELETE /api/collecteurs/{collecteur_id}
```

**Réponse :** 204 No Content

### 6. Connexion/Déconnexion

```http
PATCH /api/collecteurs/{collecteur_id}/connexion
PATCH /api/collecteurs/{collecteur_id}/deconnexion
```

**Réponse :** 200 OK avec l'objet mis à jour

---

## 💰 COLLECTES

### 1. Liste des collectes

```http
GET /api/collectes
```

**Paramètres de requête (optionnels) :**
- `skip` (int) : Pagination
- `limit` (int) : Nombre d'éléments (défaut: 100, max: 1000)
- `collecteur_id` (int) : Filtrer par collecteur
- `contribuable_id` (int) : Filtrer par contribuable
- `taxe_id` (int) : Filtrer par taxe
- `statut` (string) : `pending`, `completed`, `failed`, `cancelled`
- `date_debut` (date) : Format `YYYY-MM-DD`
- `date_fin` (date) : Format `YYYY-MM-DD`
- `telephone` (string) : Recherche par téléphone du contribuable

**Exemple :**
```http
GET /api/collectes?collecteur_id=1&statut=completed&date_debut=2024-01-01
```

**Réponse :**
```json
[
  {
    "id": 1,
    "contribuable_id": 5,
    "taxe_id": 2,
    "collecteur_id": 1,
    "montant": 10000.00,
    "commission": 500.00,
    "reference": "COL-20240115-0001",
    "type_paiement": "especes",
    "statut": "completed",
    "date_collecte": "2024-01-15T14:30:00",
    "billetage": "1x5000, 2x2000, 1x1000",
    "annule": false,
    "contribuable": {
      "id": 5,
      "nom": "MVE",
      "prenom": "Luc",
      "telephone": "+241 066 12 34 56"
    },
    "taxe": {
      "id": 2,
      "nom": "Taxe de Marché Journalière",
      "montant": 10000.00
    },
    "collecteur": {
      "id": 1,
      "nom": "Dupont",
      "prenom": "Jean",
      "matricule": "COL-001"
    }
  }
]
```

### 2. Détails d'une collecte

```http
GET /api/collectes/{collecte_id}
```

**Réponse :** Même format que la liste

### 3. Créer une collecte

```http
POST /api/collectes
Content-Type: application/json
```

**Body :**
```json
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

**Réponse :** 201 Created avec l'objet créé

### 4. Modifier une collecte

```http
PUT /api/collectes/{collecte_id}
Content-Type: application/json
```

**Body :** Mêmes champs que la création (tous optionnels)

### 5. Valider une collecte

```http
PATCH /api/collectes/{collecte_id}/valider
```

**Réponse :** 200 OK avec l'objet mis à jour (statut = `completed`)

### 6. Annuler une collecte

```http
PATCH /api/collectes/{collecte_id}/annuler
```

**Body (optionnel) :**
```json
{
  "raison": "Erreur de saisie"
}
```

**Réponse :** 200 OK avec l'objet mis à jour (annule = true)

---

## 📊 TAXES

### 1. Liste des taxes

```http
GET /api/taxes
```

**Paramètres de requête (optionnels) :**
- `skip` (int) : Pagination
- `limit` (int) : Nombre d'éléments (défaut: 100, max: 1000)
- `actif` (bool) : Filtrer par statut actif
- `type_taxe_id` (int) : Filtrer par type de taxe
- `service_id` (int) : Filtrer par service

**Exemple :**
```http
GET /api/taxes?actif=true
```

**Réponse :**
```json
[
  {
    "id": 1,
    "nom": "Taxe de Marché Journalière",
    "code": "TAX-001",
    "description": "Taxe quotidienne pour les vendeurs de marché",
    "montant": 1000.00,
    "montant_variable": false,
    "periodicite": "journaliere",
    "commission_pourcentage": 5.0,
    "actif": true,
    "type_taxe_id": 1,
    "service_id": 1,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
]
```

### 2. Détails d'une taxe

```http
GET /api/taxes/{taxe_id}
```

**Réponse :** Même format que la liste

### 3. Créer une taxe

```http
POST /api/taxes
Content-Type: application/json
```

**Body :**
```json
{
  "nom": "Taxe de Marché Journalière",
  "code": "TAX-001",
  "description": "Taxe quotidienne pour les vendeurs de marché",
  "montant": 1000.00,
  "montant_variable": false,
  "periodicite": "journaliere",
  "commission_pourcentage": 5.0,
  "actif": true,
  "type_taxe_id": 1,
  "service_id": 1
}
```

**Réponse :** 201 Created avec l'objet créé

### 4. Modifier une taxe

```http
PUT /api/taxes/{taxe_id}
Content-Type: application/json
```

**Body :** Mêmes champs que la création (tous optionnels)

### 5. Supprimer une taxe

```http
DELETE /api/taxes/{taxe_id}
```

**Note :** Soft delete (actif = false)

**Réponse :** 204 No Content

---

## 🔍 ENDPOINTS UTILES POUR MOBILE

### 1. Collectes d'un collecteur (avec pagination)

```http
GET /api/collectes?collecteur_id=1&limit=20&skip=0
```

### 2. Statistiques d'un collecteur

```http
GET /api/rapports/collecteur/{collecteur_id}
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

### 3. Contribuables d'un collecteur

```http
GET /api/contribuables?collecteur_id=1&actif=true
```

### 4. Taxes actives

```http
GET /api/taxes?actif=true&limit=100
```

---

## 📝 Codes de statut HTTP

- `200` : Succès
- `201` : Créé avec succès
- `204` : Supprimé avec succès
- `400` : Requête invalide
- `401` : Non authentifié
- `403` : Accès interdit
- `404` : Ressource non trouvée
- `422` : Erreur de validation
- `500` : Erreur serveur

---

## 🧪 Tester l'API

### Avec Swagger UI

Accédez à : `https://votre-app.onrender.com/docs`

### Avec cURL

```bash
# Login
curl -X POST "https://votre-app.onrender.com/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=votre_mot_de_passe"

# Liste des collecteurs
curl -X GET "https://votre-app.onrender.com/api/collecteurs?actif=true" \
  -H "Authorization: Bearer VOTRE_TOKEN"
```

---

## 📱 Exemple d'intégration mobile (Flutter/Dart)

```dart
// Service API
class ApiService {
  final String baseUrl = 'https://votre-app.onrender.com';
  String? token;

  Future<Map<String, dynamic>> login(String email, String password) async {
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
      return data;
    }
    throw Exception('Échec de la connexion');
  }

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
    throw Exception('Erreur lors de la récupération des collecteurs');
  }

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
    throw Exception('Erreur lors de la création de la collecte');
  }
}
```

---

## 🔗 Liens utiles

- **Documentation Swagger :** `https://votre-app.onrender.com/docs`
- **Documentation ReDoc :** `https://votre-app.onrender.com/redoc`
- **Health Check :** `https://votre-app.onrender.com/health`

