"""
Script QGIS : Créer des zones depuis OpenStreetMap
À exécuter dans la Console Python de QGIS
Nécessite le plugin QuickOSM
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

def create_zones_from_osm():
    """
    Télécharge et crée des zones depuis OpenStreetMap
    Nécessite le plugin QuickOSM installé
    """
    
    try:
        # Vérifier si QuickOSM est disponible
        from QuickOSM.core.utilities.tools import get_setting
        from QuickOSM.definitions.osm import QueryType
        from QuickOSM.core.query_factory import QueryFactory
        from QuickOSM.core.utilities.tools import get_processing_algorithm
        
        # Paramètres pour Libreville
        place = "Libreville, Gabon"
        key = "boundary"
        value = "administrative"
        query_type = QueryType.Overpass
        
        # Créer la requête
        query_factory = QueryFactory()
        query = query_factory.build_query(
            query_type=query_type,
            key=key,
            value=value,
            area=place
        )
        
        # Exécuter la requête
        QgsMessageLog.logMessage("📡 Téléchargement des données OSM...", "OSM", Qgis.Info)
        
        # Utiliser l'algorithme de traitement QuickOSM
        alg = get_processing_algorithm("quickosm:queryoverpassapi")
        if alg:
            params = {
                'QUERY': query,
                'TIMEOUT': 25,
                'EXTENT': None
            }
            processing.run("quickosm:queryoverpassapi", params)
            QgsMessageLog.logMessage("✅ Zones téléchargées depuis OSM", "OSM", Qgis.Success)
        else:
            QgsMessageLog.logMessage("❌ Plugin QuickOSM non disponible", "OSM", Qgis.Warning)
            return False
            
    except ImportError:
        QgsMessageLog.logMessage(
            "❌ Plugin QuickOSM requis. Installez-le via Extensions → Installer/Gérer les extensions",
            "OSM",
            Qgis.Warning
        )
        return False
    except Exception as e:
        QgsMessageLog.logMessage(f"❌ Erreur: {str(e)}", "OSM", Qgis.Critical)
        return False

# Exécuter
# create_zones_from_osm()

