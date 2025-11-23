"""
Script Python : Créer un fichier CSV d'exemple pour importer des contribuables
"""

import csv
import random

# Coordonnées approximatives de Libreville
LIBREVILLE_CENTER = {
    "lat": 0.3901,
    "lng": 9.4542
}

# Noms et prénoms gabonais d'exemple
NOMS = ["MVE", "MINTSA", "MBOUMBA", "NDONG", "OBAME", "MBOUMBA", "NDONG", "BOUKAMBA", "MBOUMBA", "NDONG"]
PRENOMS = ["Luc", "Anne", "David", "Jean", "Marc", "Marie", "Paul", "Sophie", "Pierre", "Julie"]

def generate_phone():
    """Génère un numéro de téléphone gabonais"""
    return f"+241 066 {random.randint(10, 99)} {random.randint(10, 99)} {random.randint(10, 99)}"

def generate_coordinates():
    """Génère des coordonnées aléatoires autour de Libreville"""
    lat = LIBREVILLE_CENTER["lat"] + random.uniform(-0.05, 0.05)
    lng = LIBREVILLE_CENTER["lng"] + random.uniform(-0.05, 0.05)
    return lat, lng

def create_sample_csv(filename="contribuables_sample.csv", count=20):
    """Crée un fichier CSV d'exemple"""
    
    activites = [
        "Épicerie du Centre",
        "Restaurant Chez Marie",
        "Boutique de vêtements",
        "Pharmacie Centrale",
        "Café du Marché",
        "Boulangerie Artisanale",
        "Salon de coiffure",
        "Garage Auto",
        "Bureau de change",
        "Magasin d'électronique"
    ]
    
    adresses = [
        "Avenue Léon Mba, N° 45",
        "Boulevard Triomphal, N° 12",
        "Rue de la Paix, N° 8",
        "Avenue du Port, N° 23",
        "Boulevard de l'Indépendance, N° 67",
        "Rue des Écoles, N° 15",
        "Avenue de la République, N° 34",
        "Boulevard de la Mer, N° 9"
    ]
    
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        
        # En-têtes
        writer.writerow([
            "nom", "prenom", "telephone", "adresse", 
            "nom_activite", "latitude", "longitude"
        ])
        
        # Données
        for i in range(count):
            lat, lng = generate_coordinates()
            writer.writerow([
                random.choice(NOMS),
                random.choice(PRENOMS),
                generate_phone(),
                random.choice(adresses),
                random.choice(activites),
                f"{lat:.6f}",
                f"{lng:.6f}"
            ])
    
    print(f"✅ Fichier CSV créé: {filename}")
    print(f"   {count} contribuables générés")
    print(f"\n📝 Pour l'importer dans QGIS:")
    print(f"   1. Ouvrez QGIS")
    print(f"   2. Couche → Ajouter une couche → Ajouter une couche de texte délimité")
    print(f"   3. Sélectionnez le fichier: {filename}")
    print(f"   4. Définissez longitude=X, latitude=Y")
    print(f"   5. CRS: EPSG:4326 (WGS 84)")

if __name__ == "__main__":
    import sys
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    create_sample_csv(count=count)

