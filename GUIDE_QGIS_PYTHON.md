# 🗺️ Guide : Créer des cartes avec QGIS et Python

Ce guide vous explique comment créer et exporter des données géographiques depuis QGIS vers votre application de gestion de taxes.

## 📋 Table des matières

1. [Installation et configuration](#installation)
2. [Créer des zones géographiques (polygones)](#zones)
3. [Créer des points (contribuables)](#points)
4. [Exporter vers PostgreSQL/PostGIS](#export-postgres)
5. [Exporter vers GeoJSON](#export-geojson)
6. [Scripts Python avec PyQGIS](#pyqgis)
7. [Importer dans l'application](#import-app)

---

## 🔧 1. Installation et configuration {#installation}

### Prérequis

- **QGIS** : Téléchargez depuis https://qgis.org/
- **PostgreSQL avec PostGIS** : Déjà installé pour votre application
- **Python 3.x** : Déjà installé

### Configuration de la connexion PostgreSQL dans QGIS

1. Ouvrez QGIS
2. Allez dans **Couche** → **Ajouter une couche** → **Ajouter une couche PostGIS**
3. Cliquez sur **Nouveau** pour créer une connexion
4. Remplissez les informations :
   ```
   Nom : Taxe Municipale
   Hôte : localhost
   Port : 5432
   Base de données : taxe_municipale
   Utilisateur : postgres
   Mot de passe : [votre mot de passe]
   ```
5. Testez la connexion et sauvegardez

---

## 🗺️ 2. Créer des zones géographiques (polygones) {#zones}

### Méthode 1 : Créer manuellement dans QGIS

1. **Créer une nouvelle couche**
   - **Couche** → **Créer une couche** → **Nouvelle couche Shapefile**
   - Choisissez **Polygone** comme type de géométrie
   - Définissez le CRS : **WGS 84 (EPSG:4326)**
   - Ajoutez les champs :
     - `nom` (Texte, 100)
     - `type_zone` (Texte, 50) - ex: "quartier", "arrondissement"
     - `code` (Texte, 50) - optionnel
     - `actif` (Booléen)
   - Enregistrez le fichier (ex: `zones_libreville.shp`)

2. **Dessiner les zones**
   - Activez l'édition (icône crayon)
   - Utilisez l'outil **Ajouter une entité polygone**
   - Cliquez pour créer les points du polygone
   - Double-cliquez pour terminer
   - Remplissez les attributs dans le formulaire

3. **Dessiner depuis une carte satellite**
   - Ajoutez une couche XYZ : **Couche** → **Ajouter une couche** → **Ajouter une couche XYZ**
   - URL : `https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}`
   - Utilisez cette couche comme fond de carte pour dessiner précisément

### Méthode 2 : Importer depuis OpenStreetMap

1. **Installer le plugin QuickOSM**
   - **Extensions** → **Installer/Gérer les extensions**
   - Recherchez "QuickOSM" et installez-le

2. **Télécharger des zones**
   - **Vectoriel** → **QuickOSM** → **QuickOSM**
   - Sélectionnez "Quartier" ou "Arrondissement"
   - Choisissez la zone (Libreville)
   - Téléchargez et importez

---

## 📍 3. Créer des points (contribuables) {#points}

### Méthode 1 : Créer manuellement

1. **Créer une nouvelle couche de points**
   - **Couche** → **Créer une couche** → **Nouvelle couche Shapefile**
   - Type : **Point**
   - CRS : **WGS 84 (EPSG:4326)**
   - Champs :
     - `nom` (Texte, 100)
     - `prenom` (Texte, 100)
     - `telephone` (Texte, 20)
     - `adresse` (Texte, 255)
     - `nom_activite` (Texte, 200)

2. **Ajouter des points**
   - Activez l'édition
   - Utilisez l'outil **Ajouter une entité point**
   - Cliquez sur la carte à l'emplacement du contribuable
   - Remplissez les attributs

### Méthode 2 : Importer depuis un fichier CSV

1. **Préparer un fichier CSV** avec colonnes :
   ```csv
   nom,prenom,telephone,adresse,latitude,longitude
   MVE,Luc,+241 066 12 34 56,Avenue Léon Mba,0.3901,9.4542
   MINTSA,Anne,+241 066 23 45 67,Boulevard Triomphal,0.4100,9.4700
   ```

2. **Importer dans QGIS**
   - **Couche** → **Ajouter une couche** → **Ajouter une couche de texte délimité**
   - Sélectionnez votre fichier CSV
   - Définissez `longitude` comme X et `latitude` comme Y
   - CRS : **WGS 84 (EPSG:4326)**

---

## 🗄️ 4. Exporter vers PostgreSQL/PostGIS {#export-postgres}

### Méthode 1 : Via l'interface QGIS

1. **Clic droit sur la couche** → **Exporter** → **Sauvegarder les entités sous**
2. Choisissez **PostgreSQL** comme format
3. Sélectionnez votre connexion
4. Nom de la table : `zone_geographique` ou `contribuable`
5. **Options importantes** :
   - ✅ **Créer une table spatiale**
   - ✅ **Créer un index spatial**
   - CRS : **EPSG:4326**
6. Cliquez sur **OK**

### Méthode 2 : Via Python (PyQGIS)

Créez un script Python dans QGIS :

```python
# Script QGIS : exporter_vers_postgres.py
from qgis.core import QgsVectorLayer, QgsVectorFileWriter, QgsCoordinateReferenceSystem

# Charger la couche
layer = iface.activeLayer()

# Paramètres de connexion PostgreSQL
uri = "postgresql://postgres:VOTRE_MOT_DE_PASSE@localhost:5432/taxe_municipale?sslmode=disable"

# Options d'export
options = QgsVectorFileWriter.SaveVectorOptions()
options.driverName = "PostgreSQL"
options.fileEncoding = "UTF-8"

# Exporter
error = QgsVectorFileWriter.writeAsVectorFormatV2(
    layer,
    uri,
    QgsCoordinateTransformContext(),
    options
)

if error[0] == QgsVectorFileWriter.NoError:
    print("✅ Export réussi!")
else:
    print(f"❌ Erreur: {error}")
```

**Comment utiliser :**
1. Ouvrez la **Console Python** dans QGIS (Extension → Console Python)
2. Collez le script
3. Modifiez les paramètres (mot de passe, nom de table)
4. Exécutez

---

## 📄 5. Exporter vers GeoJSON {#export-geojson}

### Via l'interface QGIS

1. **Clic droit sur la couche** → **Exporter** → **Sauvegarder les entités sous**
2. Format : **GeoJSON**
3. Nom du fichier : `zones_libreville.geojson`
4. CRS : **EPSG:4326**
5. Cliquez sur **OK**

### Via Python

```python
# Script : exporter_geojson.py
from qgis.core import QgsVectorFileWriter, QgsCoordinateReferenceSystem

layer = iface.activeLayer()
output_file = "C:/chemin/vers/zones_libreville.geojson"

options = QgsVectorFileWriter.SaveVectorOptions()
options.driverName = "GeoJSON"
options.fileEncoding = "UTF-8"

error = QgsVectorFileWriter.writeAsVectorFormatV2(
    layer,
    output_file,
    QgsCoordinateTransformContext(),
    options
)

if error[0] == QgsVectorFileWriter.NoError:
    print(f"✅ Exporté vers {output_file}")
else:
    print(f"❌ Erreur: {error}")
```

---

## 🐍 6. Scripts Python avec PyQGIS {#pyqgis}

### Script 1 : Créer des zones depuis un fichier CSV

```python
# create_zones_from_csv.py
from qgis.core import QgsVectorLayer, QgsFeature, QgsGeometry, QgsPointXY, QgsField, QgsProject
from qgis.PyQt.QtCore import QVariant
import csv

# Créer une nouvelle couche de polygones
layer = QgsVectorLayer("Polygon?crs=EPSG:4326", "Zones", "memory")
provider = layer.dataProvider()

# Ajouter les champs
provider.addAttributes([
    QgsField("nom", QVariant.String),
    QgsField("type_zone", QVariant.String),
    QgsField("code", QVariant.String),
    QgsField("actif", QVariant.Bool)
])
layer.updateFields()

# Lire le CSV et créer les zones
with open("zones.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        # Créer un polygone simple (carré pour l'exemple)
        # Vous pouvez adapter pour créer des polygones complexes
        lat = float(row["latitude"])
        lng = float(row["longitude"])
        size = 0.01  # Taille du polygone en degrés
        
        points = [
            QgsPointXY(lng - size, lat - size),
            QgsPointXY(lng + size, lat - size),
            QgsPointXY(lng + size, lat + size),
            QgsPointXY(lng - size, lat + size),
            QgsPointXY(lng - size, lat - size)  # Fermer le polygone
        ]
        
        geom = QgsGeometry.fromPolygonXY([points])
        feature = QgsFeature()
        feature.setGeometry(geom)
        feature.setAttributes([
            row["nom"],
            row["type_zone"],
            row.get("code", ""),
            True
        ])
        provider.addFeature(feature)

layer.updateExtents()
QgsProject.instance().addMapLayer(layer)
print("✅ Couche créée!")
```

### Script 2 : Importer des points depuis CSV

```python
# import_points_from_csv.py
from qgis.core import QgsVectorLayer, QgsFeature, QgsGeometry, QgsPointXY, QgsField
from qgis.PyQt.QtCore import QVariant
import csv

# Créer une couche de points
layer = QgsVectorLayer("Point?crs=EPSG:4326", "Contribuables", "memory")
provider = layer.dataProvider()

# Ajouter les champs
provider.addAttributes([
    QgsField("nom", QVariant.String),
    QgsField("prenom", QVariant.String),
    QgsField("telephone", QVariant.String),
    QgsField("adresse", QVariant.String)
])
layer.updateFields()

# Lire le CSV
with open("contribuables.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        point = QgsPointXY(float(row["longitude"]), float(row["latitude"]))
        geom = QgsGeometry.fromPointXY(point)
        
        feature = QgsFeature()
        feature.setGeometry(geom)
        feature.setAttributes([
            row["nom"],
            row.get("prenom", ""),
            row["telephone"],
            row.get("adresse", "")
        ])
        provider.addFeature(feature)

layer.updateExtents()
QgsProject.instance().addMapLayer(layer)
print("✅ Points importés!")
```

### Script 3 : Exporter vers PostgreSQL avec transformation

```python
# export_to_postgres.py
from qgis.core import QgsVectorLayer, QgsVectorFileWriter, QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsProject

layer = iface.activeLayer()

# Paramètres PostgreSQL
uri = "postgresql://postgres:VOTRE_MOT_DE_PASSE@localhost:5432/taxe_municipale?sslmode=disable&table=zone_geographique&geometrycolumn=geom"

# Options
options = QgsVectorFileWriter.SaveVectorOptions()
options.driverName = "PostgreSQL"
options.fileEncoding = "UTF-8"
options.layerName = "zone_geographique"

# Exporter
error = QgsVectorFileWriter.writeAsVectorFormatV2(
    layer,
    uri,
    QgsCoordinateTransformContext(),
    options
)

if error[0] == QgsVectorFileWriter.NoError:
    print("✅ Export réussi vers PostgreSQL!")
else:
    print(f"❌ Erreur: {error}")
```

---

## 🔄 7. Importer dans l'application {#import-app}

### Option 1 : Via l'API (GeoJSON)

1. **Exporter depuis QGIS en GeoJSON**
2. **Utiliser l'endpoint d'import** de votre API :

```python
# import_geojson.py
import requests
import json

# Lire le fichier GeoJSON
with open("zones_libreville.geojson", "r", encoding="utf-8") as f:
    geojson_data = json.load(f)

# Envoyer à l'API
api_url = "http://localhost:8000/api/zones-geographiques"
headers = {
    "Authorization": "Bearer VOTRE_TOKEN",
    "Content-Type": "application/json"
}

for feature in geojson_data["features"]:
    zone_data = {
        "nom": feature["properties"].get("nom", ""),
        "type_zone": feature["properties"].get("type_zone", "quartier"),
        "geometry": feature["geometry"],
        "actif": True
    }
    
    response = requests.post(api_url, json=zone_data, headers=headers)
    if response.status_code == 201:
        print(f"✅ Zone {zone_data['nom']} créée")
    else:
        print(f"❌ Erreur: {response.text}")
```

### Option 2 : Directement dans PostgreSQL

Si vous avez exporté directement vers PostgreSQL depuis QGIS, les données sont déjà dans la base !

Vérifiez avec :
```sql
SELECT id, nom, type_zone, ST_AsGeoJSON(geom) as geometry 
FROM zone_geographique 
WHERE actif = true;
```

---

## 📝 Exemple complet : Workflow recommandé

### Étape 1 : Préparer les données dans QGIS

1. Créer une couche de polygones pour les quartiers
2. Dessiner les quartiers sur la carte satellite
3. Remplir les attributs (nom, code, etc.)

### Étape 2 : Exporter vers PostgreSQL

```python
# Dans la console Python de QGIS
layer = iface.activeLayer()
uri = "postgresql://postgres:VOTRE_MOT_DE_PASSE@localhost:5432/taxe_municipale?sslmode=disable&table=zone_geographique&geometrycolumn=geom"

options = QgsVectorFileWriter.SaveVectorOptions()
options.driverName = "PostgreSQL"
options.fileEncoding = "UTF-8"

error = QgsVectorFileWriter.writeAsVectorFormatV2(
    layer,
    uri,
    QgsCoordinateTransformContext(),
    options
)
```

### Étape 3 : Vérifier dans la base de données

```sql
-- Vérifier que les zones sont bien importées
SELECT id, nom, type_zone, ST_AsText(geom) 
FROM zone_geographique 
LIMIT 5;
```

### Étape 4 : Utiliser dans l'application

Les zones sont maintenant disponibles via l'API :
```
GET http://localhost:8000/api/zones-geographiques
```

---

## 🎯 Conseils pratiques

1. **CRS (Système de coordonnées)** : Toujours utiliser **EPSG:4326 (WGS 84)** pour la compatibilité
2. **Encodage** : Utiliser **UTF-8** pour les caractères spéciaux
3. **Validation** : Vérifier les géométries avant l'export (`Couche → Vérifier la validité`)
4. **Performance** : Pour de grandes quantités de données, utilisez des scripts Python plutôt que l'interface graphique

---

## 📚 Ressources supplémentaires

- Documentation QGIS : https://docs.qgis.org/
- PyQGIS Cookbook : https://docs.qgis.org/latest/en/docs/pyqgis_developer_cookbook/
- PostGIS Documentation : https://postgis.net/documentation/

---

## 🆘 Dépannage

### Problème : Les géométries ne s'affichent pas
- Vérifiez que le CRS est correct (EPSG:4326)
- Vérifiez que PostGIS est bien installé : `SELECT PostGIS_version();`

### Problème : Erreur de connexion PostgreSQL
- Vérifiez les paramètres de connexion
- Vérifiez que PostgreSQL accepte les connexions depuis QGIS
- Testez la connexion dans pgAdmin d'abord

### Problème : Caractères spéciaux mal encodés
- Utilisez UTF-8 partout
- Vérifiez l'encodage du fichier CSV/Shapefile

