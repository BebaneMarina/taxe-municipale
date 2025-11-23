# 🎯 Prochaines étapes - Déploiement sur Render

Vous avez créé la base de données PostgreSQL. Voici les étapes suivantes :

## ✅ Étape 1 : Base de données créée

Vous avez déjà :
- ✅ Hostname : `dpg-d4hac1qli9vc73e32ru0-a`
- ✅ Port : `5432`
- ✅ Database : `taxe_municipale`
- ✅ Username : `taxe_municipale_user`
- ✅ Password : `q72VWjL8s1dJT18MG0odumckupqKg7qj`
- ✅ Internal Database URL : `postgresql://taxe_municipale_user:q72VWjL8s1dJT18MG0odumckupqKg7qj@dpg-d4hac1qli9vc73e32ru0-a:5432/taxe_municipale`

## 🚀 Étape 2 : Créer le service Web

### 2.1 Créer un nouveau service Web

1. Dans le dashboard Render, cliquez sur **"New +"** en haut à droite
2. Sélectionnez **"Web Service"**
3. Connectez votre repository Git :
   - Si c'est la première fois : Cliquez sur **"Connect account"** et autorisez Render
   - Sélectionnez votre repository : `e_taxe_back_office`
   - Sélectionnez la branche : `main` (ou `master`)

### 2.2 Configuration du service

Remplissez les champs suivants :

**Basic Settings :**
- **Name** : `e-taxe-api` (ou le nom de votre choix)
- **Environment** : `Python 3`
- **Region** : Choisissez la région la plus proche (ex: `Frankfurt` ou `Oregon`)

**Build & Deploy :**
- **Build Command** : `cd backend && pip install -r requirements.txt`
- **Start Command** : `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`

⚠️ **Important** : Si votre `main.py` est dans le dossier `backend/`, utilisez les commandes ci-dessus avec `cd backend &&`.

Si `main.py` est à la racine, utilisez :
- **Build Command** : `pip install -r backend/requirements.txt`
- **Start Command** : `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

### 2.3 Variables d'environnement

Cliquez sur **"Advanced"** → **"Add Environment Variable"** et ajoutez :

#### Variable 1 : DATABASE_URL
- **Key** : `DATABASE_URL`
- **Value** : `postgresql://taxe_municipale_user:q72VWjL8s1dJT18MG0odumckupqKg7qj@dpg-d4hac1qli9vc73e32ru0-a:5432/taxe_municipale`
- ⚠️ **Copiez l'Internal Database URL** depuis votre page de base de données (c'est l'URL complète)

#### Variable 2 : SECRET_KEY
- **Key** : `SECRET_KEY`
- **Value** : Générez une clé secrète aléatoire (ex: `votre-cle-secrete-tres-longue-et-securisee-123456789`)
- Ou laissez Render la générer automatiquement

#### Variable 3 (Optionnel) : PYTHON_VERSION
- **Key** : `PYTHON_VERSION`
- **Value** : `3.11.0`

#### Variable 4 (Optionnel) : CORS_ORIGINS
- **Key** : `CORS_ORIGINS`
- **Value** : `*` (pour permettre toutes les origines, ou spécifiez les URLs de votre app mobile)

### 2.4 Créer le service

1. Vérifiez toutes les configurations
2. Cliquez sur **"Create Web Service"**
3. Render va automatiquement :
   - Cloner votre repository
   - Installer les dépendances
   - Démarrer l'application

## ⏳ Étape 3 : Attendre le déploiement

Le déploiement prend généralement **2-5 minutes**.

Vous pouvez suivre la progression dans les **"Logs"** :
- Cliquez sur votre service web
- Onglet **"Logs"**
- Vous verrez les étapes de build et de démarrage

## ✅ Étape 4 : Vérifier le déploiement

Une fois déployé, vous obtiendrez une URL : `https://e-taxe-api.onrender.com` (ou similaire)

### 4.1 Test de santé

Ouvrez dans votre navigateur ou testez avec curl :
```bash
curl https://e-taxe-api.onrender.com/health
```

**Réponse attendue :**
```json
{"status": "healthy"}
```

### 4.2 Documentation Swagger

Ouvrez dans votre navigateur :
```
https://e-taxe-api.onrender.com/docs
```

Vous devriez voir l'interface Swagger avec tous vos endpoints.

### 4.3 Test de connexion à la base de données

L'application devrait se connecter automatiquement à la base de données au démarrage.

Vérifiez les logs pour voir :
```
✅ Base de données initialisée
```

## 🔧 Dépannage

### Problème : Erreur de build

**Symptôme** : Le build échoue dans les logs

**Solution** :
1. Vérifiez que `requirements.txt` existe dans `backend/`
2. Vérifiez que toutes les dépendances sont listées
3. Vérifiez les logs pour voir l'erreur exacte

### Problème : Erreur de connexion à la base de données

**Symptôme** : Erreur dans les logs concernant PostgreSQL

**Solution** :
1. Vérifiez que `DATABASE_URL` est correcte (copiez l'Internal Database URL)
2. Vérifiez que le mot de passe ne contient pas d'espaces
3. Vérifiez que la base de données est active dans Render

### Problème : Service ne démarre pas

**Symptôme** : Le service démarre puis s'arrête

**Solution** :
1. Vérifiez les logs pour l'erreur exacte
2. Vérifiez que `main.py` est au bon endroit
3. Vérifiez que le `Start Command` est correct

### Problème : Port déjà utilisé

**Symptôme** : Erreur "Port already in use"

**Solution** :
- Utilisez toujours `$PORT` dans le Start Command (Render le définit automatiquement)

## 📝 Checklist

- [ ] Service Web créé sur Render
- [ ] Repository Git connecté
- [ ] Build Command configuré
- [ ] Start Command configuré
- [ ] Variable `DATABASE_URL` ajoutée (avec Internal Database URL)
- [ ] Variable `SECRET_KEY` ajoutée
- [ ] Service déployé avec succès
- [ ] Health check fonctionne (`/health`)
- [ ] Documentation Swagger accessible (`/docs`)
- [ ] Base de données connectée (vérifié dans les logs)

## 🎉 Une fois déployé

Votre API sera accessible à :
- **URL de base** : `https://e-taxe-api.onrender.com`
- **Documentation** : `https://e-taxe-api.onrender.com/docs`
- **Health check** : `https://e-taxe-api.onrender.com/health`

⚠️ **Note importante** : 
- Le service gratuit se met en veille après 15 minutes d'inactivité
- Le premier démarrage après veille peut prendre 30-60 secondes
- Pour un service 24/7, upgrade vers un plan payant

## 📤 Prochaine étape : Partager avec votre collaborateur

Une fois déployé, suivez le guide : `GUIDE_PARTAGE_COLLABORATEUR.md`

