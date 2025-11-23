"""
Script QGIS : Exporter une couche vers GeoJSON
À exécuter dans la Console Python de QGIS
"""

from qgis.core import (
    QgsVectorFileWriter,
    QgsCoordinateTransformContext,
    QgsMessageLog,
    Qgis
)
import os

def export_to_geojson(output_path=None):
    """
    Exporte la couche active vers GeoJSON
    
    Args:
        output_path: Chemin du fichier de sortie (optionnel)
    """
    
    # Récupérer la couche active
    layer = iface.activeLayer()
    
    if not layer:
        QgsMessageLog.logMessage("❌ Aucune couche sélectionnée", "Export", Qgis.Warning)
        return False
    
    # Définir le chemin de sortie si non fourni
    if not output_path:
        layer_name = layer.name().replace(" ", "_")
        output_path = f"C:/temp/{layer_name}.geojson"
    
    # Créer le dossier si nécessaire
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Options d'export
    options = QgsVectorFileWriter.SaveVectorOptions()
    options.driverName = "GeoJSON"
    options.fileEncoding = "UTF-8"
    
    # Exporter
    error = QgsVectorFileWriter.writeAsVectorFormatV2(
        layer,
        output_path,
        QgsCoordinateTransformContext(),
        options
    )
    
    if error[0] == QgsVectorFileWriter.NoError:
        QgsMessageLog.logMessage(f"✅ Exporté vers {output_path}", "Export", Qgis.Success)
        iface.messageBar().pushMessage("Export GeoJSON", f"Fichier créé: {output_path}", Qgis.Success, duration=5)
        return True
    else:
        error_msg = f"❌ Erreur: {error}"
        QgsMessageLog.logMessage(error_msg, "Export", Qgis.Critical)
        iface.messageBar().pushMessage("Erreur", error_msg, Qgis.Critical, duration=10)
        return False

# Exécuter
# export_to_geojson("C:/temp/zones_libreville.geojson")

