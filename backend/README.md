# Backend FastAPI - Collecte Taxe Municipale

API REST pour la gestion de la collecte de taxes municipales de la Mairie de Libreville.

## Installation

1. Créer un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

3. Configurer la base de données :
- Créer une base de données PostgreSQL nommée `taxe_municipale`
- Copier `.env.example` vers `.env` et modifier la configuration

4. Initialiser la base de données :
```bash
python -m database.seeders
```

5. (Optionnel mais recommandé) Activer PostGIS pour la cartographie :
```bash
psql taxe_municipale < database/sql/postgis_setup.sql
```
Ce script :
- active l'extension `postgis`
- ajoute les colonnes `geom` (points/polygones)
- synchronise les données existantes à partir des coordonnées/GeoJSON

> ⚠️ Après modification des colonnes, redémarrer l'API pour recharger les modèles SQLAlchemy.

## Démarrage

```bash
uvicorn main:app --reload --port 8000
```

L'API sera accessible sur `http://localhost:8000`
Documentation interactive : `http://localhost:8000/docs`

## Structure

- `database/` : Modèles SQLAlchemy et configuration DB
- `schemas/` : Schémas Pydantic pour la validation
- `routers/` : Routes FastAPI par entité
- `main.py` : Application FastAPI principale

## Endpoints principaux

- `/api/taxes` : Gestion des taxes
- `/api/contribuables` : Gestion des contribuables
- `/api/collecteurs` : Gestion des collecteurs
- `/api/collectes` : Gestion des collectes
- `/api/references` : Données de référence (zones, quartiers, types, etc.)

