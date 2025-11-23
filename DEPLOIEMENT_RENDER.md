# 🚀 Guide de déploiement sur Render

Guide complet pour déployer l'API FastAPI sur Render et partager l'accès avec votre collaborateur.

## 📋 Prérequis

1. Compte Render : https://render.com (gratuit)
2. Repository Git (GitHub, GitLab, ou Bitbucket)
3. Base de données PostgreSQL (Render ou externe)

---

## 🔧 Étape 1 : Préparer le projet

### 1.1 Créer les fichiers nécessaires

Créez ces fichiers à la racine du projet `backend/` :

#### `render.yaml` (Configuration Render)

```yaml
services:
  - type: web
    name: e-taxe-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        sync: false
      - key: SECRET_KEY
        generateValue: true
      - key: PYTHON_VERSION
        value: 3.11.0
    healthCheckPath: /health
```

#### `requirements.txt` (si pas déjà présent)

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
python-dotenv==1.0.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
pydantic==2.5.0
pydantic-settings==2.1.0
```

#### `.renderignore` (optionnel)

```
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
.env
*.log
.git/
.gitignore
```

---

## 🗄️ Étape 2 : Créer la base de données PostgreSQL sur Render

1. **Connectez-vous à Render** : https://dashboard.render.com
2. **Nouvelle base de données** :
   - Cliquez sur **"New +"** → **"PostgreSQL"**
   - Nom : `e-taxe-db`
   - Plan : **Free** (ou payant selon vos besoins)
   - Région : Choisissez la plus proche
   - Cliquez sur **"Create Database"**

3. **Récupérer les informations de connexion** :
   - Une fois créée, cliquez sur votre base de données
   - Notez :
     - **Hostname**
     - **Database**
     - **Port**
     - **Username**
     - **Password** (cliquez sur "Show" pour voir)

4. **Format de l'URL de connexion** :
   ```
   postgresql://username:password@hostname:port/database
   ```

---

## 🌐 Étape 3 : Déployer l'API

### 3.1 Préparer le repository Git

```bash
# Dans le dossier backend
git init
git add .
git commit -m "Initial commit for Render deployment"
git remote add origin https://github.com/votre-username/e-taxe-backend.git
git push -u origin main
```

### 3.2 Créer le service Web sur Render

1. **Nouveau service Web** :
   - Cliquez sur **"New +"** → **"Web Service"**
   - Connectez votre repository Git
   - Sélectionnez le repository et la branche (`main`)

2. **Configuration** :
   - **Name** : `e-taxe-api`
   - **Environment** : `Python 3`
   - **Build Command** : `pip install -r requirements.txt`
   - **Start Command** : `uvicorn main:app --host 0.0.0.0 --port $PORT`

3. **Variables d'environnement** :
   - Cliquez sur **"Environment"**
   - Ajoutez :
     ```
     DATABASE_URL = postgresql://username:password@hostname:port/database
     SECRET_KEY = votre-secret-key-tres-long-et-securise
     PYTHON_VERSION = 3.11.0
     ```
   - ⚠️ **Important** : Utilisez l'URL complète de la base de données créée à l'étape 2

4. **Déployer** :
   - Cliquez sur **"Create Web Service"**
   - Render va automatiquement :
     - Cloner votre repository
     - Installer les dépendances
     - Démarrer l'application

5. **URL de l'API** :
   - Une fois déployé, vous obtiendrez une URL : `https://e-taxe-api.onrender.com`
   - ⚠️ **Note** : Le service gratuit se met en veille après 15 minutes d'inactivité
   - Le premier démarrage peut prendre 30-60 secondes

---

## 👥 Étape 4 : Partager l'accès avec votre collaborateur

### 4.1 Partager l'URL de l'API

Envoyez-lui :
- **URL de l'API** : `https://e-taxe-api.onrender.com`
- **Documentation Swagger** : `https://e-taxe-api.onrender.com/docs`
- **Documentation ReDoc** : `https://e-taxe-api.onrender.com/redoc`

### 4.2 Créer un utilisateur pour le collaborateur

**Option 1 : Via l'API (recommandé)**

```bash
# Créer un utilisateur via l'API
curl -X POST "https://e-taxe-api.onrender.com/api/auth/register" \
  -H "Authorization: Bearer VOTRE_TOKEN_ADMIN" \
  -H "Content-Type: application/json" \
  -d '{
    "nom": "Collaborateur",
    "prenom": "Mobile",
    "email": "mobile@example.com",
    "password": "mot_de_passe_securise",
    "telephone": "+241 066 00 00 00",
    "role": "collecteur"
  }'
```

**Option 2 : Directement dans la base de données**

Connectez-vous à PostgreSQL et exécutez :
```sql
-- Créer un utilisateur (nécessite le hash du mot de passe)
-- Utilisez l'endpoint /api/auth/register si possible
```

### 4.3 Partager les identifiants

Envoyez à votre collaborateur :
- **Email** : `mobile@example.com`
- **Mot de passe** : `mot_de_passe_securise`
- **URL de l'API** : `https://e-taxe-api.onrender.com`

---

## 🗄️ Étape 5 : Partager l'accès à la base de données

### Option 1 : Accès via Render (Recommandé)

1. **Dans le dashboard Render** :
   - Allez sur votre base de données PostgreSQL
   - Cliquez sur **"Connections"** ou **"Info"**
   - Copiez les informations de connexion

2. **Partager avec le collaborateur** :
   - Envoyez-lui :
     - Hostname
     - Port
     - Database name
     - Username
     - Password
   - ⚠️ **Sécurisé** : Utilisez un canal sécurisé (chiffré)

### Option 2 : Créer un utilisateur PostgreSQL dédié

```sql
-- Se connecter en tant qu'admin
CREATE USER collaborateur_mobile WITH PASSWORD 'mot_de_passe_securise';
GRANT CONNECT ON DATABASE taxe_municipale TO collaborateur_mobile;
GRANT USAGE ON SCHEMA public TO collaborateur_mobile;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO collaborateur_mobile;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO collaborateur_mobile;
```

---

## 🔒 Étape 6 : Sécurité et CORS

### 6.1 Mettre à jour CORS dans `main.py`

```python
# Mettre à jour pour accepter les requêtes depuis l'app mobile
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://127.0.0.1:4200",
        "https://votre-app-mobile.com",  # URL de l'app mobile si déployée
        "*"  # ⚠️ En développement seulement, restreindre en production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 6.2 Variables d'environnement sensibles

Ne jamais commiter :
- `.env`
- `SECRET_KEY`
- `DATABASE_URL` avec mot de passe

Utilisez les variables d'environnement de Render.

---

## 📊 Étape 7 : Vérifier le déploiement

### 7.1 Tests de base

```bash
# Health check
curl https://e-taxe-api.onrender.com/health

# Documentation
# Ouvrir dans le navigateur : https://e-taxe-api.onrender.com/docs

# Test de login
curl -X POST "https://e-taxe-api.onrender.com/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=votre_mot_de_passe"
```

### 7.2 Vérifier les logs

Dans Render Dashboard :
- Allez sur votre service web
- Cliquez sur **"Logs"**
- Vérifiez qu'il n'y a pas d'erreurs

---

## 🔄 Étape 8 : Mises à jour automatiques

Render déploie automatiquement à chaque push sur la branche `main`.

Pour mettre à jour :
```bash
git add .
git commit -m "Mise à jour de l'API"
git push origin main
```

Render va automatiquement redéployer.

---

## ⚙️ Configuration avancée

### Activer le service 24/7 (Payant)

Le plan gratuit met le service en veille après 15 minutes. Pour éviter cela :
- Upgrade vers un plan payant
- Ou utiliser un service de "ping" pour maintenir le service actif

### Base de données externe

Si vous utilisez une base de données externe (non Render) :
1. Assurez-vous qu'elle est accessible depuis Internet
2. Configurez le firewall pour autoriser les connexions depuis Render
3. Utilisez l'URL complète dans `DATABASE_URL`

---

## 📝 Checklist de déploiement

- [ ] Repository Git créé et poussé
- [ ] Base de données PostgreSQL créée sur Render
- [ ] Service Web créé sur Render
- [ ] Variables d'environnement configurées
- [ ] CORS mis à jour pour l'app mobile
- [ ] Utilisateur créé pour le collaborateur
- [ ] Documentation API partagée
- [ ] Tests de base effectués
- [ ] Logs vérifiés

---

## 🆘 Dépannage

### Problème : Service ne démarre pas

1. Vérifiez les logs dans Render Dashboard
2. Vérifiez que `requirements.txt` est complet
3. Vérifiez que `main.py` est à la racine du dossier backend
4. Vérifiez les variables d'environnement

### Problème : Erreur de connexion à la base de données

1. Vérifiez que `DATABASE_URL` est correcte
2. Vérifiez que la base de données est active
3. Vérifiez que le mot de passe est correct (pas d'espaces)

### Problème : CORS errors dans l'app mobile

1. Mettez à jour `allow_origins` dans `main.py`
2. Redéployez l'application
3. Vérifiez que les headers sont corrects

---

## 📞 Support

- **Documentation Render** : https://render.com/docs
- **Support Render** : support@render.com
- **Status Render** : https://status.render.com

