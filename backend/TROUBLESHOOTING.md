# 🔧 Guide de Dépannage

## ❌ Erreur : 'utf-8' codec can't decode byte

Cette erreur se produit généralement quand :
1. Le mot de passe PostgreSQL contient des caractères spéciaux
2. Le fichier `.env` n'est pas en UTF-8
3. L'encodage système Windows cause des problèmes

### Solution 1 : Encoder le mot de passe dans .env

Si votre mot de passe PostgreSQL contient des caractères spéciaux (comme `@`, `#`, `%`, etc.), encodez-le dans le fichier `.env` :

**Exemple :**
```env
# Mot de passe : "mon@mot#passe"
# Encodé :
DATABASE_URL=postgresql://postgres:mon%40mot%23passe@localhost:5432/taxe_municipale
```

**Caractères à encoder :**
- `@` → `%40`
- `#` → `%23`
- `%` → `%25`
- `&` → `%26`
- `+` → `%2B`
- `=` → `%3D`
- `?` → `%3F`

### Solution 2 : Utiliser le script de correction

```bash
python -m database.fix_encoding
```

Ce script corrige automatiquement l'URL dans le fichier `.env`.

### Solution 3 : Changer le mot de passe PostgreSQL

Si possible, utilisez un mot de passe sans caractères spéciaux :

```sql
ALTER USER postgres WITH PASSWORD 'nouveaumotdepasse';
```

Puis mettez à jour le `.env` :
```env
DATABASE_URL=postgresql://postgres:nouveaumotdepasse@localhost:5432/taxe_municipale
```

### Solution 4 : Vérifier la connexion

Testez d'abord la connexion :
```bash
python -m database.check_connection
```

## 🔍 Autres Problèmes Courants

### Erreur : "Module not found"

**Solution :**
```bash
# Vérifiez que l'environnement virtuel est activé
# Vous devriez voir (venv) au début de votre ligne

# Réinstallez les dépendances
pip install -r requirements.txt
```

### Erreur : "psycopg2-binary ne s'installe pas"

**Windows :**
1. Installez Visual Studio Build Tools
2. Ou utilisez : `pip install psycopg2-binary --only-binary :all:`

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

### Erreur : "Base de données n'existe pas"

**Solution :**
```sql
CREATE DATABASE taxe_municipale;
```

### Erreur : "Tables déjà existent"

**Solution :**
Le script vérifie les doublons, donc vous pouvez relancer sans problème. Si vous voulez tout réinitialiser :

```sql
-- ATTENTION : Supprime TOUTES les données !
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;
```

Puis relancez :
```bash
python -m database.init_db
python -m database.run_seeders
```

## ✅ Vérification Étape par Étape

1. **Test de connexion :**
   ```bash
   python -m database.check_connection
   ```

2. **Vérifier le fichier .env :**
   - Existe-t-il dans `backend/.env` ?
   - Est-il en UTF-8 ?
   - Le mot de passe est-il correctement encodé ?

3. **Vérifier PostgreSQL :**
   ```bash
   psql -U postgres -d taxe_municipale
   ```

4. **Vérifier les tables :**
   ```sql
   \dt
   ```

## 📞 Support

Si le problème persiste :
1. Vérifiez les logs d'erreur complets
2. Testez la connexion avec `check_connection.py`
3. Vérifiez que toutes les dépendances sont installées

