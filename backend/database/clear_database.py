"""
Script pour vider toutes les tables de la base de données
"""

from database.database import engine, SessionLocal
from sqlalchemy import text
from database.models import (
    InfoCollecte, AffectationTaxe, Contribuable, Collecteur,
    Taxe, TypeTaxe, Service, Quartier, Zone, TypeContribuable, Utilisateur
)

def clear_database():
    """Vide toutes les tables de la base de données"""
    db = SessionLocal()
    try:
        print("🗑️  Vidage de la base de données...")
        
        # Désactiver temporairement les contraintes de clés étrangères
        db.execute(text("SET session_replication_role = 'replica';"))
        
        # Supprimer dans l'ordre pour respecter les foreign keys
        tables = [
            "info_collecte",
            "affectation_taxe",
            "contribuable",
            "collecteur",
            "taxe",
            "utilisateur",
            "type_taxe",
            "service",
            "quartier",
            "zone",
            "type_contribuable"
        ]
        
        for table in tables:
            try:
                result = db.execute(text(f"TRUNCATE TABLE {table} CASCADE;"))
                print(f"✅ Table {table} vidée")
            except Exception as e:
                print(f"⚠️  Erreur pour {table}: {e}")
        
        # Réactiver les contraintes
        db.execute(text("SET session_replication_role = 'origin';"))
        db.commit()
        
        print("\n✅ Base de données vidée avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur lors du vidage: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print("⚠️  ATTENTION: Cette opération va supprimer TOUTES les données!")
    response = input("Êtes-vous sûr de vouloir continuer? (oui/non): ")
    if response.lower() in ['oui', 'o', 'yes', 'y']:
        clear_database()
    else:
        print("❌ Opération annulée")

