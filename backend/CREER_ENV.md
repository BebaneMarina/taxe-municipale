# 📝 Création du Fichier .env

## 🎯 Fichier .env Créé Automatiquement

Le fichier `.env` a été créé dans `backend/.env` avec la configuration par défaut.

## ⚙️ Configuration

Ouvrez `backend/.env` et modifiez selon votre configuration PostgreSQL :

```env
DATABASE_URL=postgresql://postgres:VOTRE_MOT_DE_PASSE@localhost:5432/taxe_municipale
```

**Remplacez :**
- `postgres` par votre utilisateur PostgreSQL
- `VOTRE_MOT_DE_PASSE` par votre mot de passe PostgreSQL

## 🔐 Si votre mot de passe contient des caractères spéciaux

Encodez-les dans l'URL :
- `@` → `%40`
- `#` → `%23`
- `%` → `%25`
- `&` → `%26`

**Exemple :**
```env
# Si votre mot de passe est "mon@mot#passe"
DATABASE_URL=postgresql://postgres:mon%40mot%23passe@localhost:5432/taxe_municipale
```

## ✅ Après Configuration

1. Testez la connexion :
   ```powershell
   python -m database.check_connection
   ```

2. Si ça fonctionne, insérez les données :
   ```powershell
   python -m database.run_seeders 100
   ```

## 🐛 Si le problème persiste

Exécutez le script de correction :
```powershell
python -m database.fix_encoding
```

Il corrigera automatiquement l'encodage dans le fichier .env.

