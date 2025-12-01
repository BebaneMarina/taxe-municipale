# 📋 Guide d'Exécution des Migrations SQL

## 🎯 Ordre d'Exécution Recommandé

### Étape 1 : Initialisation PostGIS (OBLIGATOIRE EN PREMIER)
```powershell
psql -U postgres -W -d taxe_municipale -f database\migrations\00_setup_complete.sql
```
**OU** (si vous préférez utiliser le script original) :
```powershell
psql -U postgres -W -d taxe_municipale -f database\sql\postgis_setup.sql
```

**Ce script :**
- Active l'extension PostGIS
- Ajoute les colonnes `geom` à : `zone_geographique`, `contribuable`, `collecteur`, `quartier`
- Synchronise les données existantes

---

### Étape 2 : Créer la vue de cartographie
```powershell
psql -U postgres -W -d taxe_municipale -f database\migrations\create_view_cartographie_contribuable.sql
```

**Ce script :**
- Crée la vue `cartographie_contribuable_view` pour la carte interactive
- Calcule les statistiques de paiement et de collecte

---

### Étape 3 : Générer les coordonnées des quartiers (OPTIONNEL)
```powershell
python scripts\generate_fake_coordinates.py
```

**Ce script :**
- Génère des coordonnées GPS pour les quartiers sans géolocalisation
- Met à jour les colonnes `geom` des quartiers

---

## 📝 Autres Migrations Disponibles

### Tables de transactions BambooPay
```powershell
psql -U postgres -W -d taxe_municipale -f database\migrations\create_transaction_bamboopay.sql
```

### Tables de caisses
```powershell
psql -U postgres -W -d taxe_municipale -f database\migrations\create_caisses_tables.sql
```

### Tables de relances
```powershell
psql -U postgres -W -d taxe_municipale -f database\migrations\create_relances_impayes.sql
```

---

## ⚠️ Résolution des Erreurs

### Erreur : "la colonne q.geom n'existe pas"
**Solution :** Exécutez d'abord `00_setup_complete.sql` pour ajouter la colonne `geom` à la table `quartier`.

### Erreur : "l'extension postgis existe déjà"
**C'est normal**, le script utilise `CREATE EXTENSION IF NOT EXISTS`, donc il continue.

### Erreur : "la colonne geom existe déjà"
**C'est normal**, le script utilise `ADD COLUMN IF NOT EXISTS`, donc il continue.

---

## ✅ Vérification

Pour vérifier que tout est correct :
```sql
-- Vérifier que PostGIS est activé
SELECT PostGIS_version();

-- Vérifier que les colonnes geom existent
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name IN ('quartier', 'contribuable', 'collecteur', 'zone_geographique')
  AND column_name = 'geom';

-- Vérifier que la vue existe
SELECT * FROM cartographie_contribuable_view LIMIT 5;
```

