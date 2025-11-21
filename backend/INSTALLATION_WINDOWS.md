# 🪟 Installation sur Windows

## 📋 Prérequis

- Python 3.9 ou supérieur ([Télécharger ici](https://www.python.org/downloads/))
- PostgreSQL installé ([Télécharger ici](https://www.postgresql.org/download/windows/))
- Git Bash ou PowerShell

## 🚀 Installation Rapide

### Option 1 : Script Automatique (Recommandé)

1. Ouvrez PowerShell ou CMD dans le dossier `backend`
2. Exécutez :
```cmd
install.bat
```

Le script va :
- ✅ Créer l'environnement virtuel
- ✅ Activer l'environnement
- ✅ Installer toutes les dépendances

### Option 2 : Installation Manuelle

#### Étape 1 : Ouvrir PowerShell dans le dossier backend

```powershell
cd backend
```

#### Étape 2 : Créer l'environnement virtuel

```powershell
python -m venv venv
```

#### Étape 3 : Activer l'environnement virtuel

```powershell
venv\Scripts\activate
```

Vous devriez voir `(venv)` au début de votre ligne.

#### Étape 4 : Installer les dépendances

```powershell
pip install -r requirements.txt
```

**Si pip n'est pas reconnu, utilisez :**
```powershell
python -m pip install -r requirements.txt
```

## ⚙️ Configuration

### 1. Créer la base de données PostgreSQL

Ouvrez pgAdmin ou psql et exécutez :
```sql
CREATE DATABASE taxe_municipale;
```

### 2. Créer le fichier .env

Dans le dossier `backend`, créez un fichier `.env` :

```env
DATABASE_URL=postgresql://postgres:VOTRE_MOT_DE_PASSE@localhost:5432/taxe_municipale
```

Remplacez `VOTRE_MOT_DE_PASSE` par votre mot de passe PostgreSQL.

### 3. Initialiser la base de données

```powershell
python -m database.init_db
```

### 4. Insérer les données

```powershell
python -m database.run_seeders
```

### 5. Démarrer le serveur

```powershell
uvicorn main:app --reload --port 8000
```

## ✅ Vérification

Ouvrez votre navigateur :
- **API** : http://localhost:8000
- **Documentation** : http://localhost:8000/docs
- **Health Check** : http://localhost:8000/health

## 🐛 Dépannage Windows

### Erreur : "python n'est pas reconnu"

1. Vérifiez que Python est installé :
   ```powershell
   python --version
   ```

2. Si non reconnu, ajoutez Python au PATH :
   - Ouvrez "Variables d'environnement"
   - Ajoutez Python au PATH système

### Erreur : "psycopg2-binary ne s'installe pas"

Installez Visual Studio Build Tools :
1. Téléchargez depuis : https://visualstudio.microsoft.com/downloads/
2. Installez "C++ build tools"
3. Relancez : `pip install -r requirements.txt`

**Alternative :**
```powershell
pip install psycopg2-binary --only-binary :all:
```

### Erreur : "venv\Scripts\activate n'existe pas"

Assurez-vous d'être dans le dossier `backend` :
```powershell
cd backend
python -m venv venv
```

### Erreur de connexion PostgreSQL

1. Vérifiez que PostgreSQL est démarré (Services Windows)
2. Vérifiez les credentials dans `.env`
3. Testez la connexion :
   ```powershell
   psql -U postgres -d taxe_municipale
   ```

## 📝 Commandes Utiles

### Activer l'environnement virtuel
```powershell
venv\Scripts\activate
```

### Désactiver l'environnement virtuel
```powershell
deactivate
```

### Voir les paquets installés
```powershell
pip list
```

### Mettre à jour pip
```powershell
python -m pip install --upgrade pip
```

## 🎯 Checklist d'Installation

- [ ] Python 3.9+ installé
- [ ] PostgreSQL installé et démarré
- [ ] Environnement virtuel créé
- [ ] Environnement virtuel activé
- [ ] Dépendances installées (`pip install -r requirements.txt`)
- [ ] Base de données créée
- [ ] Fichier `.env` configuré
- [ ] Base de données initialisée
- [ ] Données insérées
- [ ] Serveur démarré (`uvicorn main:app --reload`)

## 🚀 Une fois tout installé

Vous pouvez maintenant :
1. ✅ Utiliser l'API sur `http://localhost:8000`
2. ✅ Tester l'authentification
3. ✅ Démarrer le frontend Angular
4. ✅ Développer votre application

