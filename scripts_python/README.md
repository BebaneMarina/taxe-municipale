# 📁 Scripts Python (Standalone)

Ces scripts peuvent être exécutés depuis la ligne de commande, indépendamment de QGIS.

## 🚀 Installation des dépendances

```bash
pip install requests
```

## 📝 Scripts disponibles

### 1. `import_geojson_to_api.py`
Importe un fichier GeoJSON dans l'API via HTTP.

**Usage :**
```bash
python import_geojson_to_api.py zones.geojson http://localhost:8000/api/zones-geographiques [token]
```

**Exemple :**
```bash
python import_geojson_to_api.py zones_libreville.geojson http://localhost:8000/api/zones-geographiques
```

### 2. `create_sample_csv.py`
Génère un fichier CSV d'exemple avec des contribuables fictifs.

**Usage :**
```bash
python create_sample_csv.py [nombre]
```

**Exemple :**
```bash
python create_sample_csv.py 50
```

Génère un fichier `contribuables_sample.csv` avec 50 contribuables.

