"""
Script simple pour exécuter les seeders
Usage: python -m database.run_seeders [nombre_par_table]
"""

import sys
import os

# Définir l'encodage UTF-8 pour éviter les problèmes
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from database.database import SessionLocal, engine
from database.seeders_complet import seed_all
from sqlalchemy import text

def test_db_connection():
    """Teste la connexion avant de commencer"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"❌ Erreur de connexion à la base de données: {e}")
        print("\n💡 Solutions possibles:")
        print("   1. Vérifiez que PostgreSQL est démarré")
        print("   2. Vérifiez les credentials dans .env")
        print("   3. Si votre mot de passe contient des caractères spéciaux, encodez-le:")
        print("      Exemple: postgresql://user:mot%40passe@localhost:5432/db")
        print("   4. Exécutez: python -m database.fix_encoding")
        return False

if __name__ == "__main__":
    # Tester la connexion d'abord
    if not test_db_connection():
        sys.exit(1)
    
    db = SessionLocal()
    try:
        # Par défaut, 50 entrées par table
        count = 50
        if len(sys.argv) > 1:
            count = int(sys.argv[1])
            print(f"📊 Mode personnalisé : {count} entrées par table\n")
        else:
            print(f"📊 Mode par défaut : {count} entrées par table\n")
        
        seed_all(db, count)
        
        print("\n🎉 Toutes les données ont été insérées avec succès!")
    except UnicodeDecodeError as e:
        print(f"\n❌ Erreur d'encodage UTF-8: {e}")
        print("\n💡 Solutions:")
        print("   1. Vérifiez que votre mot de passe PostgreSQL est en ASCII")
        print("   2. Ou encodez-le dans le fichier .env")
        print("   3. Exécutez: python -m database.fix_encoding")
    except Exception as e:
        print(f"\n❌ Erreur lors du seeding: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

