# 👥 Guide de partage avec votre collaborateur

Guide rapide pour partager l'accès à l'API et la base de données avec votre collaborateur pour le développement de l'application mobile.

## 📋 Ce que votre collaborateur a besoin

1. ✅ **URL de l'API** (une fois déployée sur Render)
2. ✅ **Documentation API** (endpoints, formats, exemples)
3. ✅ **Identifiants de connexion** (email + mot de passe)
4. ✅ **Accès à la base de données** (optionnel, pour comprendre la structure)

---

## 🚀 Étape 1 : Déployer sur Render

Suivez le guide complet : **`DEPLOIEMENT_RENDER.md`**

**Résumé rapide :**
1. Créez un compte Render : https://render.com
2. Créez une base de données PostgreSQL
3. Créez un service Web et connectez votre repository Git
4. Configurez les variables d'environnement
5. Déployez !

**URL de l'API** : `https://votre-app.onrender.com`

---

## 📚 Étape 2 : Partager la documentation API

Envoyez à votre collaborateur :

1. **`API_DOCUMENTATION.md`** - Documentation complète des endpoints
2. **URL Swagger** : `https://votre-app.onrender.com/docs`
3. **URL ReDoc** : `https://votre-app.onrender.com/redoc`

### Endpoints principaux pour mobile :

- **Authentification** : `POST /api/auth/login`
- **Collecteurs** : `GET /api/collecteurs`
- **Collectes** : `GET /api/collectes`, `POST /api/collectes`
- **Taxes** : `GET /api/taxes`

---

## 🔐 Étape 3 : Créer un compte utilisateur pour le collaborateur

### Option 1 : Via l'API (Recommandé)

```bash
# 1. Connectez-vous en tant qu'admin
curl -X POST "https://votre-app.onrender.com/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=votre_mot_de_passe"

# 2. Créez un compte pour le collaborateur
curl -X POST "https://votre-app.onrender.com/api/auth/register" \
  -H "Authorization: Bearer VOTRE_TOKEN_ADMIN" \
  -H "Content-Type: application/json" \
  -d '{
    "nom": "Collaborateur",
    "prenom": "Mobile",
    "email": "mobile@example.com",
    "password": "mot_de_passe_securise_123",
    "telephone": "+241 066 00 00 00",
    "role": "collecteur"
  }'
```

### Option 2 : Via Swagger UI

1. Allez sur : `https://votre-app.onrender.com/docs`
2. Connectez-vous avec votre compte admin
3. Utilisez l'endpoint `/api/auth/register`
4. Créez le compte

### Envoyer les identifiants

Envoyez à votre collaborateur (de manière sécurisée) :
```
Email : mobile@example.com
Mot de passe : mot_de_passe_securise_123
URL API : https://votre-app.onrender.com
```

---

## 🗄️ Étape 4 : Partager l'accès à la base de données (Optionnel)

### Option 1 : Via Render Dashboard

1. Allez sur votre base de données dans Render
2. Cliquez sur **"Connections"** ou **"Info"**
3. Copiez les informations :
   - Hostname
   - Port
   - Database name
   - Username
   - Password

4. Envoyez-les à votre collaborateur (de manière sécurisée)

### Option 2 : Créer un utilisateur PostgreSQL dédié

Connectez-vous à PostgreSQL et exécutez :

```sql
-- Créer un utilisateur avec accès en lecture seule (recommandé)
CREATE USER collaborateur_mobile WITH PASSWORD 'mot_de_passe_securise';
GRANT CONNECT ON DATABASE taxe_municipale TO collaborateur_mobile;
GRANT USAGE ON SCHEMA public TO collaborateur_mobile;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO collaborateur_mobile;

-- Ou avec accès complet (si nécessaire)
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO collaborateur_mobile;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO collaborateur_mobile;
```

### Option 3 : Export du schéma SQL

Exportez uniquement le schéma (sans les données) :

```bash
pg_dump -h hostname -U username -d taxe_municipale --schema-only > schema.sql
```

Envoyez `schema.sql` à votre collaborateur.

---

## 📱 Étape 5 : Exemple d'intégration pour mobile

### Flutter/Dart

```dart
class ApiService {
  final String baseUrl = 'https://votre-app.onrender.com';
  String? token;

  Future<void> login(String email, String password) async {
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
    }
  }

  Future<List<dynamic>> getCollecteurs() async {
    final response = await http.get(
      Uri.parse('$baseUrl/api/collecteurs?actif=true'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );
    
    return json.decode(response.body);
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
    
    return json.decode(response.body);
  }
}
```

### React Native

```javascript
const API_BASE_URL = 'https://votre-app.onrender.com';

class ApiService {
  async login(email, password) {
    const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: `username=${email}&password=${password}`,
    });
    
    const data = await response.json();
    return data.access_token;
  }

  async getCollecteurs(token) {
    const response = await fetch(`${API_BASE_URL}/api/collecteurs?actif=true`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    
    return await response.json();
  }
}
```

---

## ✅ Checklist de partage

- [ ] API déployée sur Render
- [ ] URL de l'API partagée
- [ ] Documentation API envoyée (`API_DOCUMENTATION.md`)
- [ ] Compte utilisateur créé pour le collaborateur
- [ ] Identifiants envoyés (de manière sécurisée)
- [ ] Accès à la base de données partagé (si nécessaire)
- [ ] Exemples d'intégration fournis

---

## 🔒 Sécurité

### ⚠️ Important

1. **Ne partagez jamais** les identifiants admin
2. **Créez un compte dédié** pour le collaborateur avec les permissions minimales nécessaires
3. **Utilisez HTTPS** (Render le fait automatiquement)
4. **Changez les mots de passe** régulièrement
5. **Utilisez des canaux sécurisés** pour partager les identifiants (chiffrement, messagerie sécurisée)

### Recommandations

- Utilisez des mots de passe forts
- Limitez les permissions (lecture seule si possible)
- Surveillez les logs d'accès
- Activez l'authentification à deux facteurs sur Render (si disponible)

---

## 📞 Support

Si votre collaborateur rencontre des problèmes :

1. **Vérifiez les logs** dans Render Dashboard
2. **Testez l'API** avec Swagger UI
3. **Vérifiez les variables d'environnement**
4. **Consultez la documentation** : `API_DOCUMENTATION.md`

---

## 🎯 Prochaines étapes pour le collaborateur

1. ✅ Lire `API_DOCUMENTATION.md`
2. ✅ Tester l'API avec Swagger : `https://votre-app.onrender.com/docs`
3. ✅ Se connecter avec les identifiants fournis
4. ✅ Tester les endpoints principaux
5. ✅ Intégrer dans l'application mobile

