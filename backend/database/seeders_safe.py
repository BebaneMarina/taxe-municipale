"""
Version sécurisée du script de seeding qui gère les doublons
Utilise des insertions individuelles avec vérification
"""

from database.seeders_complet import *
from sqlalchemy.exc import IntegrityError

def seed_all_safe(db: Session, count_per_table=50):
    """Version sécurisée qui gère les erreurs de doublons"""
    print(f"\n🌱 Début du seeding sécurisé...")
    print(f"📊 Objectif : {count_per_table} entrées minimum par table\n")
    
    try:
        seed_zones_safe(db, count_per_table)
        seed_quartiers_safe(db, count_per_table)
        seed_types_contribuables_safe(db, count_per_table)
        seed_services_safe(db, count_per_table)
        seed_types_taxes_safe(db, count_per_table)
        seed_taxes_safe(db, count_per_table)
        seed_collecteurs_safe(db, count_per_table)
        seed_contribuables_safe(db, count_per_table)
        seed_affectations_safe(db, count_per_table)
        seed_collectes_safe(db, count_per_table)
        seed_utilisateurs_safe(db, count_per_table)
        
        print("\n🎉 Toutes les données ont été insérées avec succès!")
    except Exception as e:
        print(f"\n❌ Erreur lors du seeding: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()

def seed_zones_safe(db: Session, count=50):
    """Seed des zones avec gestion des doublons"""
    zones_created = 0
    for zone_data in ZONES_LIBREVILLE:
        try:
            zone = db.query(Zone).filter(Zone.code == zone_data["code"]).first()
            if not zone:
                zone = Zone(**zone_data)
                db.add(zone)
                db.commit()
                zones_created += 1
        except IntegrityError:
            db.rollback()
    
    # Créer des zones supplémentaires si nécessaire
    for i in range(len(ZONES_LIBREVILLE), count):
        try:
            code = f"ZONE-{str(i+1).zfill(3)}"
            existing_zone = db.query(Zone).filter(Zone.code == code).first()
            if not existing_zone:
                zone = Zone(
                    nom=f"Zone {i+1}",
                    code=code,
                    description=f"Zone géographique {i+1}",
                    actif=True
                )
                db.add(zone)
                db.commit()
                zones_created += 1
        except IntegrityError:
            db.rollback()
    
    print(f"✅ {zones_created} zones créées")

# Répéter pour les autres fonctions...
# Pour simplifier, modifions directement seeders_complet.py

