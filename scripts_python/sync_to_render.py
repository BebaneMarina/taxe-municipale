"""
Script pour synchroniser les données de la base locale vers Render
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import sys
import os

# Configuration
LOCAL_DB = {
    "host": "localhost",
    "database": "taxe_municipale",
    "user": "postgres",
    "password": os.getenv("LOCAL_DB_PASSWORD", "admin")  # Modifiez selon votre config
}

RENDER_DB = {
    "host": "dpg-d4hac1qli9vc73e32ru0-a",
    "database": "taxe_municipale",
    "user": "taxe_municipale_user",
    "password": "q72VWjL8s1dJT18MG0odumckupqKg7qj",
    "port": 5432
}

def sync_table(local_cur, render_cur, table_name, columns):
    """Synchronise une table de la base locale vers Render"""
    print(f"\n📊 Synchronisation de la table: {table_name}")
    
    # Récupérer les données de la base locale
    local_cur.execute(f"SELECT {', '.join(columns)} FROM {table_name}")
    rows = local_cur.fetchall()
    
    print(f"   📤 {len(rows)} enregistrements trouvés dans la base locale")
    
    if len(rows) == 0:
        print(f"   ⚠️ Aucune donnée à synchroniser")
        return 0
    
    # Préparer la requête d'insertion
    placeholders = ', '.join(['%s'] * len(columns))
    columns_str = ', '.join(columns)
    
    # Vérifier si la table existe dans Render
    render_cur.execute(f"""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = '{table_name}'
        );
    """)
    table_exists = render_cur.fetchone()[0]
    
    if not table_exists:
        print(f"   ⚠️ Table {table_name} n'existe pas dans Render, ignorée")
        return 0
    
    # Insérer les données (avec gestion des conflits)
    inserted = 0
    errors = 0
    
    for row in rows:
        try:
            values = [row[col] for col in columns]
            render_cur.execute(f"""
                INSERT INTO {table_name} ({columns_str})
                VALUES ({placeholders})
                ON CONFLICT DO NOTHING
            """, values)
            if render_cur.rowcount > 0:
                inserted += 1
        except Exception as e:
            errors += 1
            if errors <= 5:  # Afficher seulement les 5 premières erreurs
                print(f"   ❌ Erreur: {e}")
    
    print(f"   ✅ {inserted} enregistrements insérés")
    if errors > 0:
        print(f"   ⚠️ {errors} erreurs")
    
    return inserted

def main():
    """Fonction principale"""
    print("🔄 Synchronisation des données vers Render")
    print("=" * 50)
    
    try:
        # Connexions
        print("\n🔌 Connexion à la base locale...")
        local_conn = psycopg2.connect(**LOCAL_DB)
        local_cur = local_conn.cursor(cursor_factory=RealDictCursor)
        print("   ✅ Connecté à la base locale")
        
        print("\n🔌 Connexion à Render...")
        render_conn = psycopg2.connect(**RENDER_DB)
        render_cur = render_conn.cursor()
        print("   ✅ Connecté à Render")
        
        # Synchroniser les tables principales
        # Ajustez selon votre schéma
        
        # Contribuables
        sync_table(
            local_cur, render_cur,
            "contribuable",
            ["id", "nom", "prenom", "email", "telephone", "type_contribuable_id", 
             "quartier_id", "collecteur_id", "adresse", "latitude", "longitude", 
             "nom_activite", "photo_url", "numero_identification", "actif", 
             "created_at", "updated_at"]
        )
        
        # Collecteurs
        sync_table(
            local_cur, render_cur,
            "collecteur",
            ["id", "nom", "prenom", "matricule", "email", "telephone", 
             "statut", "etat", "zone_id", "actif", "created_at", "updated_at"]
        )
        
        # Taxes
        sync_table(
            local_cur, render_cur,
            "taxe",
            ["id", "nom", "code", "description", "montant", "montant_variable",
             "periodicite", "commission_pourcentage", "actif", "type_taxe_id",
             "service_id", "created_at", "updated_at"]
        )
        
        # Collectes
        sync_table(
            local_cur, render_cur,
            "info_collecte",
            ["id", "contribuable_id", "taxe_id", "collecteur_id", "montant",
             "commission", "reference", "type_paiement", "statut", "date_collecte",
             "billetage", "annule", "created_at", "updated_at"]
        )
        
        # Commit
        render_conn.commit()
        print("\n✅ Synchronisation terminée avec succès!")
        
    except psycopg2.OperationalError as e:
        print(f"\n❌ Erreur de connexion: {e}")
        print("\n💡 Vérifiez:")
        print("   - Que la base locale est accessible")
        print("   - Que les identifiants Render sont corrects")
        print("   - Que votre firewall autorise les connexions sortantes")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        if 'local_cur' in locals():
            local_cur.close()
        if 'local_conn' in locals():
            local_conn.close()
        if 'render_cur' in locals():
            render_cur.close()
        if 'render_conn' in locals():
            render_conn.close()

if __name__ == "__main__":
    main()

