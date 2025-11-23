# 📁 Scripts QGIS

Ces scripts sont à exécuter dans la **Console Python de QGIS**.

## 🚀 Comment utiliser

1. **Ouvrir QGIS**
2. **Ouvrir la Console Python** : `Extension` → `Console Python` (ou `Ctrl+Alt+P`)
3. **Charger un script** :
   - Cliquez sur l'icône "Ouvrir un script"
   - Sélectionnez le fichier `.py`
   - Cliquez sur "Exécuter le script"

## 📝 Scripts disponibles

### 1. `export_zones_to_postgres.py`
Exporte la couche active (polygones) vers PostgreSQL.

**Avant d'exécuter :**
- Modifiez le mot de passe PostgreSQL dans le script
- Assurez-vous qu'une couche de polygones est active

### 2. `import_points_from_csv.py`
Importe des points depuis un fichier CSV.

**Format CSV requis :**
```csv
nom,prenom,telephone,adresse,latitude,longitude
MVE,Luc,+241 066 12 34 56,Avenue Léon Mba,0.3901,9.4542
```

**Avant d'exécuter :**
- Modifiez le chemin du fichier CSV dans le script
- Le fichier doit être encodé en UTF-8

### 3. `export_to_geojson.py`
Exporte la couche active vers GeoJSON.

**Avant d'exécuter :**
- Optionnel : modifiez le chemin de sortie

### 4. `create_zones_from_osm.py`
Télécharge des zones depuis OpenStreetMap.

**Prérequis :**
- Plugin QuickOSM installé dans QGIS

