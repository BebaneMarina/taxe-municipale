# ✅ Import du dump dans Render

## 🔗 URL de connexion

```
postgresql://taxe_municipale_user:q72VWjL8sldJTl8MGOodumckupqKg7qj@dpg-d4hac1qli9vc73e32ru0-a.singapore-postgres.render.com/taxe_municipale
```

**Région** : Singapore  
**Port** : 5432 (par défaut, peut être omis)

---

## 🚀 Méthode 1 : Via psql (Ligne de commande)

### Étape 1 : Activer PostGIS (Important !)

```powershell
# Dans PowerShell
$env:PGPASSWORD="q72VWjL8sldJTl8MGOodumckupqKg7qj"
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" "postgresql://taxe_municipale_user:q72VWjL8sldJTl8MGOodumckupqKg7qj@dpg-d4hac1qli9vc73e32ru0-a.singapore-postgres.render.com:5432/taxe_municipale" -c "CREATE EXTENSION IF NOT EXISTS postgis;"
```

### Étape 2 : Importer le dump

```powershell
# Toujours dans PowerShell, depuis le dossier du projet
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" "postgresql://taxe_municipale_user:q72VWjL8sldJTl8MGOodumckupqKg7qj@dpg-d4hac1qli9vc73e32ru0-a.singapore-postgres.render.com:5432/taxe_municipale" -f backend\dump_taxe.sql
```

**Ou si psql est dans votre PATH :**

```powershell
psql "postgresql://taxe_municipale_user:q72VWjL8sldJTl8MGOodumckupqKg7qj@dpg-d4hac1qli9vc73e32ru0-a.singapore-postgres.render.com:5432/taxe_municipale" -f backend\dump_taxe.sql
```

---

## 🖥️ Méthode 2 : Via pgAdmin (Recommandé - Plus simple)

### Étape 1 : Créer la connexion

1. **Ouvrez pgAdmin**
2. **Clic droit sur "Servers"** → **Create** → **Server**
3. **Onglet "General"** :
   - **Name** : `Render Singapore`
4. **Onglet "Connection"** :
   - **Host name/address** : `dpg-d4hac1qli9vc73e32ru0-a.singapore-postgres.render.com`
   - **Port** : `5432`
   - **Maintenance database** : `taxe_municipale`
   - **Username** : `taxe_municipale_user`
   - **Password** : `q72VWjL8sldJTl8MGOodumckupqKg7qj`
   - ✅ **Cochez "Save password"**
5. **Cliquez sur "Save"**

### Étape 2 : Activer PostGIS

1. **Connectez-vous** à la base `taxe_municipale`
2. **Clic droit sur la base** → **Query Tool**
3. **Exécutez** :
   ```sql
   CREATE EXTENSION IF NOT EXISTS postgis;
   ```
4. **Exécutez** (F5)

### Étape 3 : Importer le dump

1. **Dans le Query Tool** (toujours ouvert)
2. **Ouvrez le fichier** : `backend/dump_taxe.sql`
   - Menu **File** → **Open** ou `Ctrl+O`
3. **Exécutez** le script (F5 ou bouton Play ▶️)
4. **Attendez** la fin de l'exécution (peut prendre quelques minutes)

---

## ✅ Vérification après l'import

### Via pgAdmin

Dans le Query Tool, exécutez :

```sql
-- Compter les enregistrements
SELECT 
    'contribuable' as table_name, COUNT(*) as count FROM contribuable
UNION ALL
SELECT 'collecteur', COUNT(*) FROM collecteur
UNION ALL
SELECT 'taxe', COUNT(*) FROM taxe
UNION ALL
SELECT 'info_collecte', COUNT(*) FROM info_collecte
UNION ALL
SELECT 'zone_geographique', COUNT(*) FROM zone_geographique;
```

### Via psql

```powershell
psql "postgresql://taxe_municipale_user:q72VWjL8sldJTl8MGOodumckupqKg7qj@dpg-d4hac1qli9vc73e32ru0-a.singapore-postgres.render.com:5432/taxe_municipale" -c "SELECT COUNT(*) FROM contribuable;"
```

---

## 🔧 Réinitialiser les séquenceurs (Si nécessaire)

Si vous avez des erreurs lors de la création de nouveaux enregistrements, réinitialisez les séquenceurs :

```sql
-- Dans pgAdmin Query Tool
SELECT setval('contribuable_id_seq', (SELECT MAX(id) FROM contribuable));
SELECT setval('collecteur_id_seq', (SELECT MAX(id) FROM collecteur));
SELECT setval('taxe_id_seq', (SELECT MAX(id) FROM taxe));
SELECT setval('info_collecte_id_seq', (SELECT MAX(id) FROM info_collecte));
SELECT setval('zone_geographique_id_seq', (SELECT MAX(id) FROM zone_geographique));
```

---

## ⚠️ Erreurs possibles et solutions

### Erreur : "extension postgis does not exist"
**Solution** : Activez PostGIS avant l'import (voir Étape 1)

### Erreur : "relation already exists"
**Solution** : Le dump contient des commandes `CREATE TABLE IF NOT EXISTS`, normalement ça ne devrait pas poser problème. Si oui, supprimez les tables existantes d'abord.

### Erreur : "duplicate key value"
**Solution** : Les données existent déjà. Soit supprimez-les d'abord, soit utilisez `ON CONFLICT DO NOTHING` dans le dump.

### Erreur : "could not connect to server"
**Solution** : 
- Vérifiez que vous utilisez bien l'External Database URL
- Vérifiez votre connexion Internet
- Vérifiez que le firewall n'bloque pas PostgreSQL

---

## 📝 Checklist

- [ ] PostGIS activé dans Render
- [ ] Dump importé avec succès
- [ ] Vérification du nombre d'enregistrements
- [ ] Séquenceurs réinitialisés (si nécessaire)
- [ ] Test de l'API avec les nouvelles données

---

## 🎉 Après l'import

Une fois l'import terminé :

1. **Vérifiez les données** dans pgAdmin
2. **Testez l'API** (si elle est déjà déployée) :
   ```bash
   curl https://e-taxe-api.onrender.com/api/contribuables?limit=5
   ```
3. **Partagez avec votre collaborateur** : `GUIDE_PARTAGE_COLLABORATEUR.md`

