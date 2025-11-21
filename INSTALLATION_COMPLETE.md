# 🎯 Guide d'Installation Complet

## 📦 Installation des Dépendances Python

### Méthode 1 : Script Automatique (Recommandé)

**Sur Windows :**
```bash
cd backend
install.bat
```

**Sur Linux/Mac :**
```bash
cd backend
chmod +x install.sh
./install.sh
```

### Méthode 2 : Installation Manuelle

#### Étape 1 : Aller dans le dossier backend
```bash
cd backend
```

#### Étape 2 : Créer un environnement virtuel

**Windows :**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac :**
```bash
python3 -m venv venv
source venv/bin/activate
```

Vous devriez voir `(venv)` au début de votre ligne de commande.

#### Étape 3 : Installer les dépendances
```bash
pip install -r requirements.txt
```

## 📋 Dépendances Installées

- **FastAPI** : Framework web moderne
- **Uvicorn** : Serveur ASGI
- **SQLAlchemy** : ORM pour PostgreSQL
- **psycopg2-binary** : Driver PostgreSQL
- **python-dotenv** : Gestion des variables d'environnement
- **Pydantic** : Validation des données
- **python-jose** : Authentification JWT
- **passlib** : Hashage des mots de passe

## ✅ Vérification

Vérifiez que tout est installé :
```bash
pip list
```

Vous devriez voir toutes les dépendances listées.

## 🚀 Prochaines Étapes

Une fois les dépendances installées :

1. **Configurer la base de données** :
   ```sql
   CREATE DATABASE taxe_municipale;
   ```

2. **Créer le fichier .env** :
   ```env
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/taxe_municipale
   ```

3. **Initialiser la base de données** :
   ```bash
   python -m database.init_db
   ```

4. **Insérer les données** :
   ```bash
   python -m database.run_seeders
   ```

5. **Démarrer le serveur** :
   ```bash
   uvicorn main:app --reload --port 8000
   ```

## 🐛 Problèmes Courants

### "pip n'est pas reconnu"
Utilisez `python -m pip` au lieu de `pip` :
```bash
python -m pip install -r requirements.txt
```

### "psycopg2-binary ne s'installe pas"
**Windows :** Installez Visual Studio Build Tools
**Linux :** `sudo apt-get install python3-dev libpq-dev`
**Mac :** `brew install postgresql`

### "Module not found après installation"
Assurez-vous que l'environnement virtuel est activé (vous devriez voir `(venv)`).

## 📚 Documentation

- `INSTALLATION.md` - Guide détaillé
- `QUICK_START.md` - Démarrage rapide
- `README.md` - Documentation du backend

