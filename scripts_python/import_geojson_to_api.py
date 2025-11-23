"""
Script Python : Importer un fichier GeoJSON dans l'API
À exécuter depuis la ligne de commande
"""

import requests
import json
import sys
from pathlib import Path

def import_geojson_to_api(geojson_file, api_url, token=None):
    """
    Importe un fichier GeoJSON dans l'API
    
    Args:
        geojson_file: Chemin vers le fichier GeoJSON
        api_url: URL de l'API (ex: http://localhost:8000/api/zones-geographiques)
        token: Token JWT (optionnel)
    """
    
    # Lire le fichier GeoJSON
    try:
        with open(geojson_file, "r", encoding="utf-8") as f:
            geojson_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Fichier introuvable: {geojson_file}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Erreur de parsing JSON: {e}")
        return False
    
    # Préparer les headers
    headers = {
        "Content-Type": "application/json"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    # Traiter chaque feature
    success_count = 0
    error_count = 0
    
    for feature in geojson_data.get("features", []):
        properties = feature.get("properties", {})
        geometry = feature.get("geometry", {})
        
        # Préparer les données
        zone_data = {
            "nom": properties.get("nom", f"Zone_{success_count + 1}"),
            "type_zone": properties.get("type_zone", "quartier"),
            "geometry": geometry,
            "actif": properties.get("actif", True)
        }
        
        # Ajouter les champs optionnels
        if "code" in properties:
            zone_data["code"] = properties["code"]
        if "quartier_id" in properties:
            zone_data["quartier_id"] = properties["quartier_id"]
        
        # Envoyer à l'API
        try:
            response = requests.post(api_url, json=zone_data, headers=headers)
            
            if response.status_code == 201:
                success_count += 1
                print(f"✅ Zone '{zone_data['nom']}' créée (ID: {response.json().get('id', 'N/A')})")
            elif response.status_code == 400:
                error_msg = response.json().get("detail", "Erreur inconnue")
                print(f"⚠️ Zone '{zone_data['nom']}': {error_msg}")
                error_count += 1
            else:
                print(f"❌ Zone '{zone_data['nom']}': Erreur {response.status_code} - {response.text}")
                error_count += 1
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur réseau pour '{zone_data['nom']}': {e}")
            error_count += 1
    
    # Résumé
    print(f"\n📊 Résumé:")
    print(f"   ✅ Succès: {success_count}")
    print(f"   ❌ Erreurs: {error_count}")
    print(f"   📁 Total: {len(geojson_data.get('features', []))}")
    
    return error_count == 0


if __name__ == "__main__":
    # Paramètres
    if len(sys.argv) < 2:
        print("Usage: python import_geojson_to_api.py <fichier.geojson> [api_url] [token]")
        print("\nExemple:")
        print("  python import_geojson_to_api.py zones.geojson http://localhost:8000/api/zones-geographiques")
        sys.exit(1)
    
    geojson_file = sys.argv[1]
    api_url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:8000/api/zones-geographiques"
    token = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Importer
    success = import_geojson_to_api(geojson_file, api_url, token)
    sys.exit(0 if success else 1)

