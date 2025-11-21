# 📦 Guide d'Installation - Projet Complet

## 🎯 Vue d'ensemble

Ce projet nécessite :
1. **Backend FastAPI** (Python)
2. **Frontend Angular** (Node.js)
3. **Base de données PostgreSQL**

## 🚀 Installation Rapide

### Backend (Python)

```bash
cd backend

# Windows
install.bat

# Linux/Mac
chmod +x install.sh
./install.sh
```

Puis :
```bash
# Activer l'environnement
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Configurer .env
# Créer la base de données PostgreSQL

# Initialiser
python -m database.init_db
python -m database.run_seeders

# Démarrer
uvicorn main:app --reload --port 8000
```

### Frontend (Angular)

```bash
cd e_taxe_back_office
npm install
ng serve
```

## 📚 Documentation Détaillée

- **Backend** : `backend/INSTALLATION.md` ou `backend/INSTALLATION_WINDOWS.md`
- **Frontend** : `e_taxe_back_office/README.md`
- **Base de données** : `backend/database/README_SEEDERS.md`

## ✅ Vérification

- Backend : http://localhost:8000/docs
- Frontend : http://localhost:4200
- Base de données : Connectée et peuplée

