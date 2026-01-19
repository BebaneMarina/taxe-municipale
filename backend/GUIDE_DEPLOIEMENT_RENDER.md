# 🚀 Guide Complet de Déploiement sur Render

Ce guide vous accompagne étape par étape pour déployer votre backend et votre base de données PostgreSQL sur Render.

---

## 📋 Table des matières

1. [Prérequis](#prérequis)
2. [Étape 1 : Créer la base de données PostgreSQL](#étape-1--créer-la-base-de-données-postgresql)
3. [Étape 2 : Créer le service Web (Backend)](#étape-2--créer-le-service-web-backend)
4. [Étape 3 : Configurer les variables d'environnement](#étape-3--configurer-les-variables-denvironnement)
5. [Étape 4 : Activer PostGIS (Important)](#étape-4--activer-postgis-important)
6. [Étape 5 : Initialiser la base de données](#étape-5--initialiser-la-base-de-données)
7. [Vérification du déploiement](#vérification-du-déploiement)
8. [Dépannage](#dépannage)

---

## Prérequis

- ✅ Compte Render (https://render.com)
- ✅ Repository Git (GitHub, GitLab, ou Bitbucket) avec votre code
- ✅ Accès au dashboard Render

---

## Étape 1 : Créer la base de données PostgreSQL

### 1.1. Accéder à Render Dashboard

1. Connectez-vous à https://dashboard.render.com
2. Cliquez sur **"New +"** en haut à droite
3. Sélectionnez **"PostgreSQL"**

### 1.2. Configurer la base de données

Remplissez le formulaire :

```
Name: e-taxe-db
Database: taxe_municipale
User: (laissez par défaut ou créez-en un)
Region: (choisissez la région la plus proche)
PostgreSQL Version: 15 ou supérieur (recommandé)
Plan: Free (pour tester) ou Starter/Standard (production)
```

⚠️ **Important** : Notez précieusement les informations suivantes (elles apparaîtront après la création) :
- **Internal Database URL** (format interne)
- **External Database URL** (format externe)
- **Host**
- **Port** (généralement 5432)
- **Database Name**
- **User**
- **Password**

### 1.3. Noter les informations de connexion

Après la création, vous verrez un panneau avec toutes les informations. **Copiez la "Internal Database URL"** - vous en aurez besoin pour le service Web.

Exemple de format :
```
postgresql://user:password@dpg-xxxxx-a/taxe_municipale
```

---

## Étape 2 : Créer le service Web (Backend)

### 2.1. Créer un nouveau service Web

1. Dans Render Dashboard, cliquez sur **"New +"**
2. Sélectionnez **"Web Service"**
3. Connectez votre repository Git (GitHub/GitLab/Bitbucket)

### 2.2. Configurer le service

Remplissez les informations suivantes :

```
Name: e-taxe-api
Region: (même région que la base de données)
Branch: main (ou votre branche principale)
Root Directory: backend
Environment: Python 3
Build Command: pip install -r requirements.txt
Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
Plan: Free (pour tester) ou Starter/Standard (production)
```

### 2.3. Utiliser le fichier render.yaml (Recommandé)

Au lieu de configurer manuellement, vous pouvez utiliser le fichier `render.yaml` déjà présent dans votre projet. Render le détectera automatiquement si vous :

1. Poussez votre code sur Git
2. Créez un nouveau service Web
3. Render détectera automatiquement le fichier `render.yaml`

---

## Étape 3 : Configurer les variables d'environnement

⚠️ **CRITIQUE** : Ces variables sont essentielles pour le fonctionnement de l'application.

### 3.1. Accéder aux variables d'environnement

Dans votre service Web Render :
1. Allez dans l'onglet **"Environment"**
2. Cliquez sur **"Add Environment Variable"**

### 3.2. Variables OBLIGATOIRES

#### 🔑 DATABASE_URL (Obligatoire)

```
Key: DATABASE_URL
Value: [Votre Internal Database URL de l'étape 1.3]
```

Exemple :
```
postgresql://user:password@dpg-xxxxx-a.oregon-postgres.render.com/taxe_municipale
```

⚠️ **Important** : Utilisez **"Internal Database URL"** (pas External) pour de meilleures performances et sécurité.

#### 🔐 SECRET_KEY (Obligatoire)

```
Key: SECRET_KEY
Value: [Générer une clé secrète sécurisée]
```

Pour générer une clé secrète sécurisée, vous pouvez utiliser Python :

```python
import secrets
print(secrets.token_urlsafe(32))
```

Ou simplement une chaîne aléatoire de 32+ caractères :
```
Exemple: a7f3b9c2d4e1f6g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z7
```

### 3.3. Variables OPTIONNELLES (mais recommandées)

#### 🌐 CORS_ORIGINS

```
Key: CORS_ORIGINS
Value: https://votre-frontend.com,https://votre-app-mobile.com
```

Pour le développement local :
```
http://localhost:4200,http://127.0.0.1:4200
```

#### 🏗️ ENVIRONMENT

```
Key: ENVIRONMENT
Value: production
```

#### 🔧 PYTHON_VERSION

```
Key: PYTHON_VERSION
Value: 3.11.0
```

### 3.4. Variables pour les services externes (Optionnel)

Si vous utilisez BambooPay pour les paiements :

```
BAMBOOPAY_BASE_URL=https://client.bamboopay-ga.com/api
BAMBOOPAY_MERCHANT_ID=votre_merchant_id
BAMBOOPAY_MERCHANT_SECRET=votre_merchant_secret
BAMBOOPAY_MERCHANT_USERNAME=votre_username
BAMBOOPAY_DEBUG=false
```

Si vous utilisez Ventis Messaging pour les SMS :

```
VENTIS_MESSAGING_URL=https://messaging.ventis.group/messaging/api/v1
KEYCLOAK_MESSAGING_HOST=https://signin.ventis.group
KEYCLOAK_MESSAGING_REALM=Messaging
KEYCLOAK_MESSAGING_CLIENT_ID=api-messaging
KEYCLOAK_MESSAGING_CLIENT_SECRET=votre_client_secret
KEYCLOAK_MESSAGING_USERNAME=votre_username
KEYCLOAK_MESSAGING_PASSWORD=votre_password
VENTIS_MESSAGING_SENDER=VENTIS
VENTIS_DEBUG=false
```

---

## Étape 4 : Activer PostGIS (Important)

⚠️ **Nécessaire pour la géolocalisation et la cartographie**

PostGIS n'est pas activé par défaut sur Render. Vous devez l'activer manuellement.

### 4.1. Accéder à la base de données

Dans votre base de données Render :
1. Allez dans l'onglet **"Connections"**
2. Copiez la **"External Database URL"** (temporairement)

### 4.2. Activer PostGIS via psql

Connectez-vous à votre base de données en utilisant `psql` ou un client PostgreSQL :

```bash
psql [VOTRE_EXTERNAL_DATABASE_URL]
```

Puis exécutez :

```sql
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
```

### 4.3. Vérifier l'activation

```sql
SELECT PostGIS_version();
```

Vous devriez voir la version de PostGIS installée.

---

## Étape 5 : Initialiser la base de données

### 5.1. Créer les tables

Une fois le service Web déployé, vous pouvez initialiser la base de données de deux façons :

#### Option A : Via le script Python (Recommandé)

1. Connectez-vous en SSH à votre service Web (si disponible) ou utilisez un script de migration
2. Exécutez :

```bash
python -m database.init_db
```

#### Option B : Via le script SQL

Si vous avez un fichier `database/schema.sql`, vous pouvez l'exécuter directement :

```bash
psql [VOTRE_DATABASE_URL] < database/schema.sql
```

### 5.2. Insérer les données initiales (Optionnel)

Si vous avez des seeders :

```bash
python -m database.run_seeders
```

---

## Vérification du déploiement

### 1. Health Check

Vérifiez que l'API répond :

```bash
curl https://votre-app.onrender.com/health
```

Réponse attendue :
```json
{"status": "healthy"}
```

### 2. Documentation API

Accédez à la documentation Swagger :

```
https://votre-app.onrender.com/docs
```

### 3. Tester la connexion à la base de données

Faites une requête test à un endpoint qui utilise la base de données, par exemple :

```bash
curl https://votre-app.onrender.com/api/references/zones
```

---

## Dépannage

### ❌ Erreur de connexion à la base de données

**Problème** : `could not connect to server`

**Solutions** :
1. Vérifiez que vous utilisez **Internal Database URL** (pas External) dans `DATABASE_URL`
2. Vérifiez que la base de données et le service Web sont dans la **même région**
3. Vérifiez que la base de données est **actif** (pas en veille)

### ❌ Erreur PostGIS

**Problème** : `extension "postgis" does not exist`

**Solution** : Suivez l'étape 4 pour activer PostGIS

### ❌ Service Web ne démarre pas

**Problème** : Build ou démarrage échoue

**Solutions** :
1. Vérifiez les logs dans Render Dashboard → Logs
2. Vérifiez que toutes les variables d'environnement sont définies
3. Vérifiez que `requirements.txt` est à jour
4. Vérifiez que le `Start Command` est correct

### ❌ Timeout sur Free Plan

**Problème** : Le service se met en veille après inactivité (Free Plan uniquement)

**Solution** : Le Free Plan se met en veille après 15 minutes d'inactivité. Le premier appel après veille peut prendre 30-60 secondes. Pour éviter cela, passez à un plan payant.

### ❌ Erreur d'encodage UTF-8

**Problème** : Caractères mal encodés dans la base de données

**Solution** : La configuration actuelle gère déjà UTF-8. Si le problème persiste, vérifiez que la base de données utilise l'encodage UTF-8 :

```sql
SHOW server_encoding;
```

---

## 📝 Checklist de déploiement

Avant de considérer le déploiement terminé :

- [ ] Base de données PostgreSQL créée
- [ ] Service Web créé et connecté au Git
- [ ] Variable `DATABASE_URL` configurée (Internal URL)
- [ ] Variable `SECRET_KEY` configurée (clé sécurisée)
- [ ] Variable `CORS_ORIGINS` configurée (si nécessaire)
- [ ] PostGIS activé dans la base de données
- [ ] Tables créées (via `init_db` ou `schema.sql`)
- [ ] Health check répond `/health`
- [ ] Documentation accessible `/docs`
- [ ] Tests des endpoints principaux réussis

---

## 🔗 Liens utiles

- [Documentation Render](https://render.com/docs)
- [Render PostgreSQL Guide](https://render.com/docs/databases)
- [PostGIS Documentation](https://postgis.net/documentation/)

---

## 💡 Astuces

1. **Utilisez les Internal URLs** : Plus rapides et plus sécurisées entre services Render
2. **Même région** : Gardez tous vos services dans la même région pour de meilleures performances
3. **Logs** : Surveillez les logs régulièrement dans les premiers jours
4. **Backups** : Configurez les backups automatiques pour la base de données en production
5. **Monitoring** : Utilisez les fonctionnalités de monitoring de Render

---

Bon déploiement ! 🚀

