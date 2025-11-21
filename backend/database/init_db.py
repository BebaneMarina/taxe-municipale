"""
Script pour initialiser la base de données et charger les données
"""

from database.database import init_db, SessionLocal
from database.seeders import seed_all

if __name__ == "__main__":
    print("🔧 Initialisation de la base de données...")
    init_db()
    print("✅ Tables créées")
    
    print("\n🌱 Chargement des données initiales...")
    db = SessionLocal()
    try:
        seed_all(db)
    finally:
        db.close()
    
    print("\n✅ Base de données initialisée avec succès!")
    print("\n📝 Utilisateur admin créé:")
    print("   Email: admin@mairie-libreville.ga")
    print("   Password: admin123")
    print("   ⚠️  À changer immédiatement en production !")

