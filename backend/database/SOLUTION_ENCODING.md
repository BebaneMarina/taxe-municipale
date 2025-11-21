# 🔧 Solution au Problème d'Encodage UTF-8

## ❌ Erreur Rencontrée

```
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe9 in position 103
```

## ✅ Solution Recommandée : Utiliser le Script Python

Le script Python (`seeders_complet.py`) gère mieux l'encodage que le script SQL. Utilisez-le :

```powershell
# Dans le dossier backend, avec l'environnement virtuel activé
python -m database.run_seeders 100
```

## 🔍 Si le Problème Persiste

### Étape 1 : Vérifier la Connexion

```powershell
python -m database.check_connection
```

### Étape 2 : Corriger l'Encodage du Fichier .env

Le problème vient souvent du mot de passe PostgreSQL dans le fichier `.env`.

**Option A : Encoder le mot de passe manuellement**

Si votre mot de passe est `mon@mot#passe`, dans `.env` :
```env
DATABASE_URL=postgresql://postgres:mon%40mot%23passe@localhost:5432/taxe_municipale
```

**Option B : Utiliser le script de correction**

```powershell
python -m database.fix_encoding
```

**Option C : Changer le mot de passe PostgreSQL**

Utilisez un mot de passe simple sans caractères spéciaux :
```sql
ALTER USER postgres WITH PASSWORD 'postgres123';
```

Puis dans `.env` :
```env
DATABASE_URL=postgresql://postgres:postgres123@localhost:5432/taxe_municipale
```

### Étape 3 : Relancer le Seeding

```powershell
python -m database.run_seeders 100
```

## 📝 Note sur le Script SQL

Le script SQL (`insert_data.sql`) a été corrigé pour les casts ENUM, mais le script Python reste recommandé car il gère mieux :
- ✅ L'encodage UTF-8
- ✅ Les caractères spéciaux
- ✅ Les relations entre tables
- ✅ Les doublons

## 🎯 Commandes Rapides

```powershell
# 1. Tester la connexion
python -m database.check_connection

# 2. Corriger l'encodage (si nécessaire)
python -m database.fix_encoding

# 3. Insérer les données
python -m database.run_seeders 100
```

