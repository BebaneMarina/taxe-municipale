"""
Script QGIS : Exporter les zones géographiques vers PostgreSQL/PostGIS
À exécuter dans la Console Python de QGIS
"""

from qgis.core import (
    QgsVectorFileWriter,
    QgsCoordinateTransformContext,
    QgsProject,
    QgsMessageLog,
    Qgis
)

def export_zones_to_postgres():
    """Exporte la couche active vers PostgreSQL"""
    
    # Récupérer la couche active
    layer = iface.activeLayer()
    
    if not layer:
        QgsMessageLog.logMessage("❌ Aucune couche sélectionnée", "Export", Qgis.Warning)
        return False
    
    if layer.geometryType() != QgsWkbTypes.PolygonGeometry:
        QgsMessageLog.logMessage("❌ La couche doit être de type Polygone", "Export", Qgis.Warning)
        return False
    
    # Paramètres de connexion PostgreSQL
    # ⚠️ MODIFIEZ CES PARAMÈTRES SELON VOTRE CONFIGURATION
    db_host = "localhost"
    db_port = "5432"
    db_name = "taxe_municipale"
    db_user = "postgres"
    db_password = "VOTRE_MOT_DE_PASSE"  # ⚠️ À MODIFIER
    table_name = "zone_geographique"
    geometry_column = "geom"
    
    # Construire l'URI PostgreSQL
    uri = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?sslmode=disable&table={table_name}&geometrycolumn={geometry_column}"
    
    # Options d'export
    options = QgsVectorFileWriter.SaveVectorOptions()
    options.driverName = "PostgreSQL"
    options.fileEncoding = "UTF-8"
    options.layerName = table_name
    
    # Exporter
    error = QgsVectorFileWriter.writeAsVectorFormatV2(
        layer,
        uri,
        QgsCoordinateTransformContext(),
        options
    )
    
    if error[0] == QgsVectorFileWriter.NoError:
        QgsMessageLog.logMessage(f"✅ Zones exportées vers PostgreSQL (table: {table_name})", "Export", Qgis.Success)
        iface.messageBar().pushMessage("Succès", f"Zones exportées vers {table_name}", Qgis.Success, duration=5)
        return True
    else:
        error_msg = f"❌ Erreur lors de l'export: {error}"
        QgsMessageLog.logMessage(error_msg, "Export", Qgis.Critical)
        iface.messageBar().pushMessage("Erreur", error_msg, Qgis.Critical, duration=10)
        return False

# Exécuter la fonction
if __name__ == "__main__":
    export_zones_to_postgres()

