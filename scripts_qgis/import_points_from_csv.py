"""
Script QGIS : Importer des points (contribuables) depuis un fichier CSV
À exécuter dans la Console Python de QGIS
"""

from qgis.core import (
    QgsVectorLayer,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsField,
    QgsProject,
    QgsMessageLog,
    Qgis
)
from qgis.PyQt.QtCore import QVariant
import csv
import os

def import_points_from_csv(csv_file_path):
    """
    Importe des points depuis un fichier CSV
    
    Format CSV attendu :
    nom,prenom,telephone,adresse,latitude,longitude
    MVE,Luc,+241 066 12 34 56,Avenue Léon Mba,0.3901,9.4542
    """
    
    if not os.path.exists(csv_file_path):
        QgsMessageLog.logMessage(f"❌ Fichier introuvable: {csv_file_path}", "Import", Qgis.Critical)
        return None
    
    # Créer une nouvelle couche de points
    layer = QgsVectorLayer("Point?crs=EPSG:4326", "Contribuables_Import", "memory")
    provider = layer.dataProvider()
    
    # Ajouter les champs
    provider.addAttributes([
        QgsField("nom", QVariant.String),
        QgsField("prenom", QVariant.String),
        QgsField("telephone", QVariant.String),
        QgsField("adresse", QVariant.String),
        QgsField("nom_activite", QVariant.String),
        QgsField("latitude", QVariant.Double),
        QgsField("longitude", QVariant.Double)
    ])
    layer.updateFields()
    
    # Lire le CSV et créer les points
    features_added = 0
    errors = []
    
    try:
        with open(csv_file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            
            for row_num, row in enumerate(reader, start=2):  # start=2 car ligne 1 = header
                try:
                    # Vérifier que latitude et longitude existent
                    if "latitude" not in row or "longitude" not in row:
                        errors.append(f"Ligne {row_num}: Colonnes latitude/longitude manquantes")
                        continue
                    
                    lat = float(row["latitude"])
                    lng = float(row["longitude"])
                    
                    # Vérifier que les coordonnées sont valides (Libreville approximativement)
                    if not (0.25 <= lat <= 0.65 and 9.25 <= lng <= 9.65):
                        errors.append(f"Ligne {row_num}: Coordonnées hors de Libreville (lat={lat}, lng={lng})")
                        continue
                    
                    # Créer le point
                    point = QgsPointXY(lng, lat)
                    geom = QgsGeometry.fromPointXY(point)
                    
                    # Créer la feature
                    feature = QgsFeature()
                    feature.setGeometry(geom)
                    feature.setAttributes([
                        row.get("nom", ""),
                        row.get("prenom", ""),
                        row.get("telephone", ""),
                        row.get("adresse", ""),
                        row.get("nom_activite", ""),
                        lat,
                        lng
                    ])
                    
                    provider.addFeature(feature)
                    features_added += 1
                    
                except ValueError as e:
                    errors.append(f"Ligne {row_num}: Erreur de conversion - {str(e)}")
                except Exception as e:
                    errors.append(f"Ligne {row_num}: Erreur - {str(e)}")
    
    except Exception as e:
        QgsMessageLog.logMessage(f"❌ Erreur lors de la lecture du CSV: {str(e)}", "Import", Qgis.Critical)
        return None
    
    # Mettre à jour la couche
    layer.updateExtents()
    
    # Ajouter la couche au projet
    QgsProject.instance().addMapLayer(layer)
    
    # Messages
    msg = f"✅ {features_added} points importés depuis {os.path.basename(csv_file_path)}"
    if errors:
        msg += f"\n⚠️ {len(errors)} erreurs (voir les logs)"
        for error in errors[:10]:  # Afficher les 10 premières erreurs
            QgsMessageLog.logMessage(error, "Import", Qgis.Warning)
    
    QgsMessageLog.logMessage(msg, "Import", Qgis.Success)
    iface.messageBar().pushMessage("Import CSV", msg, Qgis.Success, duration=5)
    
    return layer

# Exemple d'utilisation
# ⚠️ MODIFIEZ LE CHEMIN VERS VOTRE FICHIER CSV
csv_path = "C:/chemin/vers/votre/fichier/contribuables.csv"

# Décommentez la ligne suivante pour exécuter
# import_points_from_csv(csv_path)

