# 🚀 Démarrage Rapide

## Installation en 5 minutes

### 1. Installer les dépendances Python

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Créer la base de données

```sql
CREATE DATABASE taxe_municipale;
```

### 3. Configurer .env

Créez `backend/.env` :
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/taxe_municipale
```

### 4. Initialiser la base

```bash
python -m database.init_db
python -m database.run_seeders
```

### 5. Démarrer le serveur

```bash
uvicorn main:app --reload --port 8000
```

✅ **C'est prêt !** API disponible sur `http://localhost:8000`

## 🔐 Connexion

- **URL** : `http://localhost:8000/api/auth/login`
- **Email** : `admin@mairie-libreville.ga`
- **Mot de passe** : `admin123`

## 📚 Documentation

- API Docs : `http://localhost:8000/docs`
- Health Check : `http://localhost:8000/health`

