# Installation de la Base de Données PostgreSQL

## Option 1 : Utiliser le script SQL (Recommandé)

1. **Créer la base de données** :
```sql
CREATE DATABASE taxe_municipale;
```

2. **Exécuter le script SQL** :
```bash
psql -U postgres -d taxe_municipale -f backend/database/schema.sql
```

Ou depuis psql :
```sql
\c taxe_municipale
\i backend/database/schema.sql
```

## Option 2 : Utiliser SQLAlchemy (Automatique)

Le script Python crée automatiquement les tables :

```bash
cd backend
python -m database.init_db
```

Cette méthode :
- ✅ Crée toutes les tables
- ✅ Charge les données initiales (zones, quartiers, taxes, etc.)
- ✅ Crée l'utilisateur admin par défaut

## Vérification

Vérifier que les tables sont créées :

```sql
\dt
```

Vous devriez voir :
- service
- type_taxe
- zone
- quartier
- type_contribuable
- collecteur
- contribuable
- taxe
- affectation_taxe
- info_collecte
- utilisateur

## Utilisateur Admin

Après l'initialisation, un utilisateur admin est créé :
- **Email** : `admin@mairie-libreville.ga`
- **Mot de passe** : `admin123`
- **⚠️ À changer immédiatement en production !**

## Configuration

Dans `backend/.env` :
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/taxe_municipale
```

Ajustez selon votre configuration PostgreSQL.

