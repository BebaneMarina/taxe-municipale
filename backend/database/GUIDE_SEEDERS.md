# 🌱 Guide Complet des Seeders

## 🎯 Deux Méthodes Disponibles

### ⭐ Méthode 1 : Script Python (RECOMMANDÉ)

**Avantages :**
- ✅ Gère automatiquement l'encodage UTF-8
- ✅ Vérifie les doublons
- ✅ Gère les relations entre tables
- ✅ Plus robuste sur Windows

**Utilisation :**
```powershell
# Dans le dossier backend, avec venv activé
python -m database.run_seeders 100
```

### Méthode 2 : Script SQL

**Utilisation :**
```powershell
psql -U postgres -d taxe_municipale -f database/insert_data_fixed.sql
```

**Note :** Le script SQL original (`insert_data.sql`) a des erreurs de cast ENUM. Utilisez `insert_data_fixed.sql` qui est corrigé.

## 🔧 Résolution du Problème d'Encodage

Si vous avez l'erreur `'utf-8' codec can't decode byte` :

### Solution Rapide

1. **Utilisez le script Python** (gère mieux l'encodage) :
   ```powershell
   python -m database.run_seeders 100
   ```

2. **Ou corrigez votre fichier .env** :
   - Si votre mot de passe PostgreSQL contient `@`, encodez-le en `%40`
   - Si votre mot de passe contient `#`, encodez-le en `%23`
   - Exemple : `mon@mot#passe` → `mon%40mot%23passe`

3. **Ou utilisez le script de correction** :
   ```powershell
   python -m database.fix_encoding
   ```

## 📊 Résultat Attendu

Après exécution, vous devriez avoir :
- ✅ 50+ zones
- ✅ 50+ quartiers
- ✅ 50+ types de contribuables
- ✅ 50+ services
- ✅ 50+ types de taxes
- ✅ 50+ taxes
- ✅ 50+ collecteurs
- ✅ 50+ contribuables
- ✅ 50+ affectations
- ✅ 50+ collectes
- ✅ 50+ utilisateurs

## 🔐 Utilisateur Admin

Créé automatiquement :
- **Email** : `admin@mairie-libreville.ga`
- **Mot de passe** : `admin123`

## ✅ Vérification

Vérifiez que les données sont insérées :
```sql
SELECT COUNT(*) FROM zone;
SELECT COUNT(*) FROM contribuable;
SELECT COUNT(*) FROM collecteur;
-- etc.
```

Ou utilisez le script Python qui affiche les statistiques automatiquement.

