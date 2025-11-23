# 🔄 Synchroniser les données locales vers Render

## ⚠️ Important : Deux bases de données séparées

- **Base locale** : `localhost:5432/taxe_municipale` (sur votre machine)
- **Base Render** : `dpg-d4hac1qli9vc73e32ru0-a:5432/taxe_municipale` (sur les serveurs Render)

**Ce sont deux bases de données complètement différentes !**

Les données de votre base locale ne sont **pas automatiquement** dans Render. Il faut les exporter et les importer.

---

## 🚀 Option 1 : Exporter/Importer avec pg_dump (Recommandé)

### Étape 1 : Exporter depuis votre base locale

```bash
# Depuis votre terminal (Windows PowerShell ou CMD)
pg_dump -h localhost -U postgres -d taxe_municipale -F c -f dump_taxe_local.backup

# Ou en format SQL (plus lisible)
pg_dump -h localhost -U postgres -d taxe_municipale -f dump_taxe_local.sql
```

**Si pg_dump n'est pas dans votre PATH :**
```bash
# Chemin complet (ajustez selon votre installation PostgreSQL)
"C:\Program Files\PostgreSQL\15\bin\pg_dump.exe" -h localhost -U postgres -d taxe_municipale -f dump_taxe_local.sql
```

### Étape 2 : Importer dans Render

#### Méthode A : Via psql en ligne de commande

```bash
# Utilisez l'External Database URL depuis Render
psql "postgresql://taxe_municipale_user:q72VWjL8s1dJT18MG0odumckupqKg7qj@dpg-d4hac1qli9vc73e32ru0-a:5432/taxe_municipale" -f dump_taxe_local.sql
```

#### Méthode B : Via pgAdmin ou DBeaver

1. Créez une nouvelle connexion avec les informations Render :
   - **Host** : `dpg-d4hac1qli9vc73e32ru0-a`
   - **Port** : `5432`
   - **Database** : `taxe_municipale`
   - **Username** : `taxe_municipale_user`
   - **Password** : `q72VWjL8s1dJT18MG0odumckupqKg7qj`

2. Exécutez le fichier SQL :
   - Clic droit sur la base → **Query Tool**
   - Ouvrez `dump_taxe_local.sql`
   - Exécutez (F5)

---

## 🚀 Option 2 : Utiliser le dump existant

Si vous avez déjà un fichier `dump_taxe.sql` :

```bash
# Importer directement dans Render
psql "postgresql://taxe_municipale_user:q72VWjL8s1dJT18MG0odumckupqKg7qj@dpg-d4hac1qli9vc73e32ru0-a:5432/taxe_municipale" -f backend/dump_taxe.sql
```

---

## 🚀 Option 3 : Script Python pour synchroniser

Créez un script pour copier les données :

```python
# sync_to_render.py
import psycopg2
from psycopg2.extras import RealDictCursor
import os

# Connexion à la base locale
local_conn = psycopg2.connect(
    host="localhost",
    database="taxe_municipale",
    user="postgres",
    password="admin"  # Votre mot de passe local
)

# Connexion à la base Render
render_conn = psycopg2.connect(
    host="dpg-d4hac1qli9vc73e32ru0-a",
    database="taxe_municipale",
    user="taxe_municipale_user",
    password="q72VWjL8s1dJT18MG0odumckupqKg7qj",
    port=5432
)

local_cur = local_conn.cursor(cursor_factory=RealDictCursor)
render_cur = render_conn.cursor()

# Exemple : Copier les contribuables
print("📤 Exportation depuis la base locale...")
local_cur.execute("SELECT * FROM contribuable")
contribuables = local_cur.fetchall()

print(f"📥 Importation de {len(contribuables)} contribuables dans Render...")
for contrib in contribuables:
    # Insérer dans Render (ajustez selon votre schéma)
    render_cur.execute("""
        INSERT INTO contribuable (nom, prenom, telephone, ...)
        VALUES (%s, %s, %s, ...)
        ON CONFLICT DO NOTHING
    """, (contrib['nom'], contrib['prenom'], contrib['telephone'], ...))

render_conn.commit()
print("✅ Synchronisation terminée!")

local_cur.close()
render_cur.close()
local_conn.close()
render_conn.close()
```

---

## 🚀 Option 4 : Utiliser l'API pour migrer les données

Si vous avez beaucoup de données, vous pouvez créer un script qui :
1. Lit depuis votre base locale
2. Utilise l'API Render pour créer les enregistrements

```python
# migrate_via_api.py
import psycopg2
import requests

# Connexion locale
local_conn = psycopg2.connect("postgresql://postgres:admin@localhost:5432/taxe_municipale")
local_cur = local_conn.cursor()

# URL de l'API Render
API_URL = "https://e-taxe-api.onrender.com"

# Login pour obtenir le token
response = requests.post(f"{API_URL}/api/auth/login", data={
    "username": "admin@example.com",
    "password": "votre_mot_de_passe"
})
token = response.json()["access_token"]

headers = {"Authorization": f"Bearer {token}"}

# Migrer les contribuables
local_cur.execute("SELECT * FROM contribuable")
for contrib in local_cur.fetchall():
    data = {
        "nom": contrib[1],
        "prenom": contrib[2],
        # ... autres champs
    }
    requests.post(f"{API_URL}/api/contribuables", json=data, headers=headers)
```

---

## ⚠️ Points importants

### 1. Schéma de base de données

Assurez-vous que le schéma est identique dans les deux bases :
- Tables
- Colonnes
- Contraintes
- Index
- Extensions (PostGIS, etc.)

### 2. PostGIS

Si vous utilisez PostGIS, activez-le dans Render :

```sql
-- Dans Render, exécutez :
CREATE EXTENSION IF NOT EXISTS postgis;
```

### 3. Séquenceurs

Après l'import, réinitialisez les séquenceurs :

```sql
-- Exemple pour la table contribuable
SELECT setval('contribuable_id_seq', (SELECT MAX(id) FROM contribuable));
```

### 4. Vérification

Après l'import, vérifiez :

```sql
-- Compter les enregistrements
SELECT 
    'contribuable' as table_name, COUNT(*) as count FROM contribuable
UNION ALL
SELECT 'collecteur', COUNT(*) FROM collecteur
UNION ALL
SELECT 'taxe', COUNT(*) FROM taxe
UNION ALL
SELECT 'info_collecte', COUNT(*) FROM info_collecte;
```

---

## 🎯 Recommandation

**Pour la première fois :**
1. Utilisez **Option 1** (pg_dump) - C'est le plus simple et le plus fiable
2. Importez le dump complet dans Render
3. Vérifiez que tout fonctionne

**Pour les mises à jour futures :**
- Si vous modifiez des données localement et voulez les synchroniser, utilisez **Option 3** (script Python)
- Ou utilisez directement l'API Render pour créer/modifier les données

---

## 📝 Checklist de synchronisation

- [ ] Base de données Render créée
- [ ] PostGIS activé dans Render (si nécessaire)
- [ ] Données exportées depuis la base locale
- [ ] Données importées dans Render
- [ ] Séquenceurs réinitialisés
- [ ] Vérification du nombre d'enregistrements
- [ ] Test de l'API avec les nouvelles données

---

## 🔍 Vérifier que les données sont bien synchronisées

### Via l'API Render

```bash
# Compter les contribuables
curl https://e-taxe-api.onrender.com/api/contribuables | jq 'length'

# Voir les premiers contribuables
curl https://e-taxe-api.onrender.com/api/contribuables?limit=5
```

### Via SQL direct

Connectez-vous à Render et exécutez :
```sql
SELECT COUNT(*) FROM contribuable;
SELECT COUNT(*) FROM collecteur;
SELECT COUNT(*) FROM taxe;
```

---

## 🆘 Dépannage

### Erreur : "relation does not exist"
- Le schéma n'est pas créé dans Render
- Exécutez d'abord le script de création de schéma

### Erreur : "extension postgis does not exist"
- Activez PostGIS : `CREATE EXTENSION postgis;`

### Erreur : "duplicate key value"
- Les données existent déjà
- Utilisez `ON CONFLICT DO NOTHING` ou supprimez d'abord les données

### Erreur de connexion
- Vérifiez que vous utilisez l'**External Database URL** (pas Internal)
- Vérifiez le firewall de votre machine (autorisez les connexions sortantes)

