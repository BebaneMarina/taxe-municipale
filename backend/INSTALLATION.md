# Guide d'Installation - Backend FastAPI

## 📋 Prérequis

- Python 3.9 ou supérieur
- PostgreSQL installé et configuré
- pip (gestionnaire de paquets Python)

## 🚀 Installation Étape par Étape

### 1. Vérifier Python

```bash
python --version
# ou
python3 --version
```

Vous devriez voir Python 3.9 ou supérieur.

### 2. Aller dans le dossier backend

```bash
cd backend
```

### 3. Créer un environnement virtuel (Recommandé)

**Sur Windows :**
```bash
python -m venv venv
venv\Scripts\activate
```

**Sur Linux/Mac :**
```bash
python3 -m venv venv
source venv/bin/activate
```

Vous devriez voir `(venv)` au début de votre ligne de commande.

### 4. Installer les dépendances

```bash
pip install -r requirements.txt
```

Cela installera :
- FastAPI
- SQLAlchemy
- PostgreSQL (psycopg2)
- JWT (python-jose)
- Hashage passwords (passlib)
- Et autres dépendances...

### 5. Configurer la base de données

**Créer la base de données PostgreSQL :**

```sql
CREATE DATABASE taxe_municipale;
```

**Ou via la ligne de commande :**
```bash
createdb taxe_municipale
```

### 6. Configurer l'environnement

Créez un fichier `.env` dans le dossier `backend` :

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Modifiez le fichier `.env` si nécessaire :
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/taxe_municipale
```

Remplacez `postgres:postgres` par votre utilisateur et mot de passe PostgreSQL.

### 7. Initialiser la base de données

**Option A : Créer les tables avec SQLAlchemy**
```bash
python -m database.init_db
```

**Option B : Utiliser le script SQL**
```bash
psql -U postgres -d taxe_municipale -f database/schema.sql
```

### 8. Insérer les données

```bash
python -m database.run_seeders
```

Cela insérera 50 entrées par table avec des données gabonaises.

### 9. Démarrer le serveur

```bash
uvicorn main:app --reload --port 8000
```

Le serveur sera accessible sur : `http://localhost:8000`
Documentation API : `http://localhost:8000/docs`

## ✅ Vérification

### Tester l'API

```bash
# Health check
curl http://localhost:8000/health

# Liste des zones
curl http://localhost:8000/api/references/zones
```

### Tester l'authentification

```bash
# Connexion
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@mairie-libreville.ga&password=admin123"
```

## 🐛 Dépannage

### Erreur : "pip n'est pas reconnu"

**Windows :**
```bash
python -m pip install -r requirements.txt
```

**Linux/Mac :**
```bash
python3 -m pip install -r requirements.txt
```

### Erreur : "psycopg2-binary" ne s'installe pas

**Windows :**
Installez d'abord les outils de build :
- Téléchargez Visual Studio Build Tools
- Ou utilisez : `pip install psycopg2-binary --only-binary :all:`

**Linux :**
```bash
sudo apt-get install python3-dev libpq-dev
pip install psycopg2-binary
```

**Mac :**
```bash
brew install postgresql
pip install psycopg2-binary
```

### Erreur de connexion à PostgreSQL

1. Vérifiez que PostgreSQL est démarré :
   ```bash
   # Windows (Services)
   # Linux
   sudo systemctl status postgresql
   # Mac
   brew services list
   ```

2. Vérifiez les credentials dans `.env`

3. Testez la connexion :
   ```bash
   psql -U postgres -d taxe_municipale
   ```

### Erreur : "Module not found"

Assurez-vous que l'environnement virtuel est activé :
- Vous devriez voir `(venv)` dans votre terminal
- Réinstallez les dépendances : `pip install -r requirements.txt`

## 📝 Commandes Utiles

### Activer l'environnement virtuel

**Windows :**
```bash
venv\Scripts\activate
```

**Linux/Mac :**
```bash
source venv/bin/activate
```

### Désactiver l'environnement virtuel

```bash
deactivate
```

### Mettre à jour les dépendances

```bash
pip install --upgrade -r requirements.txt
```

### Voir les paquets installés

```bash
pip list
```

## 🎯 Prochaines Étapes

Une fois l'installation terminée :

1. ✅ Backend démarré sur `http://localhost:8000`
2. ✅ Base de données initialisée avec données
3. ✅ API accessible sur `/api/...`
4. ✅ Documentation sur `/docs`

Vous pouvez maintenant démarrer le frontend Angular !

