# Documentation API - Application Mobile

Documentation complète des endpoints pour l'application mobile.

## URL de base

**Production (Render) :** `https://taxe-municipale.onrender.com`  
**Développement :** `http://localhost:8000`

### Informations de déploiement

**Service déployé sur :** Render (https://render.com)  
**URL de l'API :** `https://taxe-municipale.onrender.com`  
**Base de données :** PostgreSQL avec PostGIS (Render)  
**Région :** Singapore  
**Statut :** En production

#### Note importante - Service gratuit Render

Le service gratuit Render se met en **veille après 15 minutes d'inactivité**. 
- Le premier démarrage après veille peut prendre **30-60 secondes**
- C'est normal, attendez simplement que le service redémarre
- Pour un service 24/7 sans veille, upgrade vers un plan payant

#### Vérifier le statut du service

```bash
# Health check
curl https://taxe-municipale.onrender.com/health

# Réponse attendue :
# {"status": "healthy"}
```

#### Documentation interactive

- **Swagger UI :** `https://taxe-municipale.onrender.com/docs`
- **ReDoc :** `https://taxe-municipale.onrender.com/redoc`
- **Health Check :** `https://taxe-municipale.onrender.com/health`

## Authentification

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

## Paiement client (BambooPay)

### Identifiants ITAXE

| Clé | Valeur |
| --- | --- |
| Nom du marchand | ITAXE |
| ID du marchand (UUID) | `9de41a58-3bd4-454e-9956-39b5b888261e` |
| **merchant_id (username Basic Auth / Numéro du marchand)** | `6008889` |
| merchant_secret (mot de passe) | `12345678` |
| Email marchand | `test@test.com` |
| Numéro de compte | `60088890901` |
| Contact | `+24174086886` |
| Date de création | `27/11/2025 12:19` |

Variables d'environnement à définir côté backend :

```env
BAMBOOPAY_BASE_URL=https://client.bamboopay-ga.com/api
BAMBOOPAY_MERCHANT_ID=6008889
BAMBOOPAY_MERCHANT_USERNAME=6008889 # facultatif, par défaut = merchant_id
BAMBOOPAY_MERCHANT_SECRET=12345678
BAMBOOPAY_MERCHANT_NAME=ITAXE
BAMBOOPAY_MERCHANT_UID=9de41a58-3bd4-454e-9956-39b5b888261e
BAMBOOPAY_MERCHANT_ACCOUNT=60088890901
BAMBOOPAY_MERCHANT_EMAIL=test@test.com
BAMBOOPAY_MERCHANT_CONTACT=+24174086886
BAMBOOPAY_DEBUG=false
```

> ⚠️ `merchant_id` **doit** contenir le **Numéro du marchand** (6008889).  
> C’est ce même identifiant qui est utilisé comme username pour l’authentification Basic `merchant_id:merchant_secret`.

### Endpoints publics

1. `GET /api/client/taxes?actif=true` — liste des taxes disponibles.
2. `POST /api/client/paiement/initier` — initier un paiement (web ou mobile instantané).
3. `GET /api/client/paiement/statut/{billing_id}` — récupérer le statut local.
4. `POST /api/client/paiement/verifier/{billing_id}` — forcer une vérification côté BambooPay.
5. `POST /api/client/paiement/callback` — endpoint appelé par BambooPay (ne nécessite pas de token).

### Exemple `POST /api/client/paiement/initier`

```json
{
  "taxe_id": 2,
  "payer_name": "Jean Dupont",
  "phone": "+24174000000",
  "matricule": "TPU-2025-001",
  "raison_sociale": "Boutique Jean & Fils",
  "payment_method": "web",
  "operateur": null
}
```

**Réponse succès (paiement web)**
```json
{
  "id": 12,
  "billing_id": "TAX-20251127-AB12CD34",
  "transaction_amount": 25000,
  "statut": "pending",
  "redirect_url": "https://client.bamboopay-ga.com/pay/redirect/TAX-20251127-AB12CD34",
  "message": "Redirection vers BambooPay..."
}
```

**Réponse succès (paiement instantané mobile)**
```json
{
  "id": 15,
  "billing_id": "TAX-20251127-EF56GH78",
  "transaction_amount": 15000,
  "statut": "pending",
  "reference_bp": "BP-8d9f03b4",
  "message": "Paiement instantané initié. Vérifiez votre téléphone."
}
```

### Vérifier un statut

```http
GET /api/client/paiement/statut/TAX-20251127-AB12CD34
```

**Réponse**
```json
{
  "id": 12,
  "billing_id": "TAX-20251127-AB12CD34",
  "reference_bp": "BP-8d9f03b4",
  "transaction_id": "TX-0000456",
  "statut": "success",
  "statut_message": "Transaction confirmée par BambooPay",
  "transaction_amount": 25000,
  "date_initiation": "2025-11-27T12:32:14.852000",
  "date_paiement": "2025-11-27T12:33:01.004000"
}
```

### Forcer une vérification côté BambooPay

```http
POST /api/client/paiement/verifier/TAX-20251127-AB12CD34
```

**Réponse**
```json
{
  "billing_id": "TAX-20251127-AB12CD34",
  "statut_local": "success",
  "statut_bamboopay": "success",
  "message": "Paiement confirmé"
}
```

---

## COLLECTEURS

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

## COLLECTES

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

## TAXES

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

## ENDPOINTS UTILES POUR MOBILE

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

## Codes de statut HTTP

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

## Tester l'API

### Avec Swagger UI

Accédez à : `https://taxe-municipale.onrender.com/docs`

### Avec cURL

```bash
# Login
curl -X POST "https://taxe-municipale.onrender.com/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=votre_mot_de_passe"

# Liste des collecteurs
curl -X GET "https://taxe-municipale.onrender.com/api/collecteurs?actif=true" \
  -H "Authorization: Bearer VOTRE_TOKEN"
```

---

## Exemple d'intégration mobile (Flutter/Dart)

```dart
// Service API
class ApiService {
  final String baseUrl = 'https://taxe-municipale.onrender.com';
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

## Liens utiles

- **Documentation Swagger :** `https://taxe-municipale.onrender.com/docs`
- **Documentation ReDoc :** `https://taxe-municipale.onrender.com/redoc`
- **Health Check :** `https://taxe-municipale.onrender.com/health`

---

## Informations de déploiement

### Environnement de production

- **Plateforme :** Render (https://render.com)
- **URL de l'API :** `https://taxe-municipale.onrender.com`
- **Base de données :** PostgreSQL avec PostGIS
- **Région :** Singapore
- **Statut :** En production et opérationnel

### Configuration technique

- **Framework :** FastAPI 0.109.0
- **Serveur :** Uvicorn avec ASGI
- **Base de données :** PostgreSQL 17.5 avec PostGIS
- **Python :** 3.11.0
- **Authentification :** JWT (JSON Web Tokens)
- **CORS :** Configuré pour accepter toutes les origines (développement)

### Service gratuit Render - Limitations

Le service gratuit Render a quelques limitations :

1. **Mise en veille automatique**
   - Le service se met en veille après **15 minutes d'inactivité**
   - Le premier démarrage après veille prend **30-60 secondes**
   - C'est normal, attendez simplement que le service redémarre

2. **Performance**
   - Limité en ressources CPU et RAM
   - Pour de meilleures performances, upgrade vers un plan payant

3. **Disponibilité**
   - Pas de garantie de disponibilité 24/7
   - Pour un service toujours actif, upgrade vers un plan payant

### Vérification du service

#### Health Check

```bash
curl https://taxe-municipale.onrender.com/health
```

**Réponse attendue :**
```json
{"status": "healthy"}
```

#### Test de connexion

```bash
# Point d'entrée de l'API
curl https://taxe-municipale.onrender.com/

# Réponse attendue :
# {
#   "message": "API Collecte Taxe Municipale - Mairie de Libreville",
#   "version": "1.0.0",
#   "docs": "/docs"
# }
```

### Monitoring

Pour surveiller le service :

1. **Render Dashboard :** https://dashboard.render.com
   - Logs en temps réel
   - Métriques de performance
   - Statut du service

2. **Logs de l'application :**
   - Accessibles via Render Dashboard
   - Affichent les erreurs et les requêtes

### Sécurité

- **HTTPS** activé automatiquement (SSL/TLS)
- **Authentification JWT** requise pour la plupart des endpoints
- **CORS** configuré (actuellement ouvert pour développement)
- **Validation des données** avec Pydantic
- **Mots de passe** hashés avec bcrypt

### Mises à jour

Les mises à jour sont automatiques via Git :

1. **Push sur GitHub** → Render détecte automatiquement
2. **Build automatique** → Installation des dépendances
3. **Déploiement automatique** → Nouvelle version en ligne

**Temps de déploiement :** ~2-5 minutes

### Variables d'environnement

Le service utilise ces variables d'environnement (configurées dans Render) :

- `DATABASE_URL` : URL de connexion PostgreSQL
- `SECRET_KEY` : Clé secrète pour JWT
- `PYTHON_VERSION` : Version Python (3.11.0)
- `CORS_ORIGINS` : Origines autorisées pour CORS

### Dépannage

#### Service ne répond pas

1. Vérifiez que le service n'est pas en veille (attendez 30-60 secondes)
2. Vérifiez les logs dans Render Dashboard
3. Testez le health check : `/health`

#### Erreur 502 Bad Gateway

- Le service est probablement en train de démarrer
- Attendez quelques secondes et réessayez

#### Erreur de connexion à la base de données

- Vérifiez les logs dans Render Dashboard
- Vérifiez que la base de données est active
- Vérifiez la variable `DATABASE_URL`

#### Erreur CORS

- Vérifiez que l'origine de votre requête est autorisée
- Vérifiez la variable `CORS_ORIGINS` dans Render

### Support

- **Documentation Render :** https://render.com/docs
- **Support Render :** support@render.com
- **Status Render :** https://status.render.com

