# 💡 Ma recommandation : Synchronisation des données

## 🎯 Méthode recommandée : pg_dump + psql

**Pourquoi cette méthode ?**
- ✅ Simple et fiable
- ✅ Préserve toutes les données (structure + contenu)
- ✅ Gère les relations, contraintes, index
- ✅ Rapide pour une première synchronisation
- ✅ Standard PostgreSQL, testé et éprouvé

---

## 📋 Étapes à suivre

### Étape 1 : Vérifier si vous avez déjà un dump

Si vous avez déjà le fichier `backend/dump_taxe.sql`, passez directement à l'**Étape 3**.

### Étape 2 : Exporter depuis votre base locale

```powershell
# Dans PowerShell (Windows)
# Remplacez "admin" par votre mot de passe PostgreSQL local
$env:PGPASSWORD="admin"
& "C:\Program Files\PostgreSQL\15\bin\pg_dump.exe" -h localhost -U postgres -d taxe_municipale -f dump_taxe_complet.sql --clean --if-exists
```

**Ou si PostgreSQL est dans votre PATH :**
```powershell
pg_dump -h localhost -U postgres -d taxe_municipale -f dump_taxe_complet.sql --clean --if-exists
```

**Options importantes :**
- `--clean` : Supprime les objets avant de les créer (évite les conflits)
- `--if-exists` : Utilise IF EXISTS pour éviter les erreurs

### Étape 3 : Importer dans Render

**Option A : Via psql en ligne de commande (Recommandé)**

```powershell
# Dans PowerShell
$env:PGPASSWORD="q72VWjL8s1dJT18MG0odumckupqKg7qj"
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -h dpg-d4hac1qli9vc73e32ru0-a -U taxe_municipale_user -d taxe_municipale -p 5432 -f dump_taxe_complet.sql
```

**Ou si psql est dans votre PATH :**
```powershell
psql "postgresql://taxe_municipale_user:q72VWjL8s1dJT18MG0odumckupqKg7qj@dpg-d4hac1qli9vc73e32ru0-a:5432/taxe_municipale" -f dump_taxe_complet.sql
```

**Option B : Via pgAdmin (Plus visuel)**

1. Ouvrez pgAdmin
2. Créez une nouvelle connexion :
   - **Name** : Render Production
   - **Host** : `dpg-d4hac1qli9vc73e32ru0-a`
   - **Port** : `5432`
   - **Database** : `taxe_municipale`
   - **Username** : `taxe_municipale_user`
   - **Password** : `q72VWjL8s1dJT18MG0odumckupqKg7qj`
3. Connectez-vous
4. Clic droit sur la base → **Query Tool**
5. Ouvrez le fichier `dump_taxe_complet.sql`
6. Exécutez (F5 ou bouton Play)

### Étape 4 : Vérifier l'import

```sql
-- Dans Render, exécutez ces requêtes pour vérifier
SELECT COUNT(*) as contribuables FROM contribuable;
SELECT COUNT(*) as collecteurs FROM collecteur;
SELECT COUNT(*) as taxes FROM taxe;
SELECT COUNT(*) as collectes FROM info_collecte;
```

Comparez avec votre base locale pour confirmer que tout est synchronisé.

---

## ⚠️ Points d'attention

### 1. PostGIS doit être activé AVANT l'import

Si votre dump contient des géométries, activez PostGIS dans Render :

```sql
-- Exécutez AVANT l'import dans Render
CREATE EXTENSION IF NOT EXISTS postgis;
```

### 2. Si vous avez des erreurs de séquenceurs

Après l'import, réinitialisez les séquenceurs :

```sql
-- Exemples (ajustez selon vos tables)
SELECT setval('contribuable_id_seq', (SELECT MAX(id) FROM contribuable));
SELECT setval('collecteur_id_seq', (SELECT MAX(id) FROM collecteur));
SELECT setval('taxe_id_seq', (SELECT MAX(id) FROM taxe));
SELECT setval('info_collecte_id_seq', (SELECT MAX(id) FROM info_collecte));
```

### 3. Si le dump est très volumineux

Pour un gros dump, utilisez le format custom (plus rapide) :

```powershell
# Export en format custom
pg_dump -h localhost -U postgres -d taxe_municipale -F c -f dump_taxe.backup

# Import en format custom
pg_restore -h dpg-d4hac1qli9vc73e32ru0-a -U taxe_municipale_user -d taxe_municipale -p 5432 dump_taxe.backup
```

---

## 🎯 Pourquoi pas les autres méthodes ?

### ❌ Script Python de synchronisation
- Plus complexe à maintenir
- Risque d'oublier certaines tables
- Plus lent pour beaucoup de données
- **Utilisez-le seulement pour des mises à jour partielles**

### ❌ Via l'API
- Très lent (une requête par enregistrement)
- Risque de timeout
- Nécessite que l'API soit déjà déployée
- **Utilisez-le seulement pour quelques enregistrements**

---

## 📝 Checklist rapide

- [ ] PostGIS activé dans Render (`CREATE EXTENSION postgis;`)
- [ ] Dump créé depuis la base locale
- [ ] Dump importé dans Render
- [ ] Vérification du nombre d'enregistrements
- [ ] Séquenceurs réinitialisés (si nécessaire)
- [ ] Test de l'API avec les nouvelles données

---

## 🚀 Après la synchronisation

Une fois les données synchronisées :

1. **Testez l'API** :
   ```bash
   curl https://e-taxe-api.onrender.com/api/contribuables?limit=5
   ```

2. **Vérifiez dans Swagger** :
   - Ouvrez : `https://e-taxe-api.onrender.com/docs`
   - Testez quelques endpoints

3. **Partagez avec votre collaborateur** :
   - L'API est maintenant prête avec les vraies données
   - Suivez `GUIDE_PARTAGE_COLLABORATEUR.md`

---

## 💡 Conseil bonus

**Pour les futures mises à jour :**
- Si vous modifiez des données localement et voulez les synchroniser, utilisez le script Python (`scripts_python/sync_to_render.py`) pour des mises à jour partielles
- Pour une resynchronisation complète, refaites un pg_dump complet

**En production :**
- Utilisez directement Render comme base principale
- Ne synchronisez plus depuis localhost
- Votre collaborateur travaillera directement avec Render

