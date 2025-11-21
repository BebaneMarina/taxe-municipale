"""
Script pour créer les types ENUM dans PostgreSQL
"""

from database.database import engine
from sqlalchemy import text

def create_enums():
    """Crée tous les types ENUM nécessaires"""
    enums = [
        ("statut_collecteur_enum", ["'active'", "'desactive'"]),
        ("etat_collecteur_enum", ["'connecte'", "'deconnecte'"]),
        ("periodicite_enum", ["'journaliere'", "'hebdomadaire'", "'mensuelle'", "'trimestrielle'"]),
        ("type_paiement_enum", ["'especes'", "'mobile_money'", "'carte'"]),
        ("statut_collecte_enum", ["'pending'", "'completed'", "'failed'", "'cancelled'"]),
        ("role_enum", ["'admin'", "'agent_back_office'", "'agent_front_office'", "'controleur_interne'", "'collecteur'"]),
    ]
    
    with engine.connect() as conn:
        for enum_name, values in enums:
            try:
                # Vérifier si l'ENUM existe déjà
                check_query = text(f"""
                    SELECT EXISTS (
                        SELECT 1 FROM pg_type WHERE typname = '{enum_name}'
                    )
                """)
                result = conn.execute(check_query)
                exists = result.scalar()
                
                if not exists:
                    # Créer l'ENUM
                    values_str = ", ".join(values)
                    create_query = text(f"CREATE TYPE {enum_name} AS ENUM ({values_str})")
                    conn.execute(create_query)
                    conn.commit()
                    print(f"✅ Type {enum_name} créé")
                else:
                    print(f"ℹ️ Type {enum_name} existe déjà")
            except Exception as e:
                print(f"❌ Erreur lors de la création de {enum_name}: {e}")
                conn.rollback()

if __name__ == "__main__":
    print("🔧 Création des types ENUM...")
    create_enums()
    print("\n✅ Terminé!")

