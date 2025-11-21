"""
Script pour vérifier la connexion à la base de données
"""

import sys
from database.database import engine, SessionLocal
from sqlalchemy import text

def test_connection():
    """Teste la connexion à la base de données"""
    try:
        print("🔍 Test de connexion à la base de données...")
        
        # Test de connexion simple
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ Connexion réussie!")
            print(f"📊 Version PostgreSQL: {version[:50]}...")
            
        # Test avec session
        db = SessionLocal()
        try:
            result = db.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';"))
            count = result.scalar()
            print(f"✅ Session fonctionnelle!")
            print(f"📋 Nombre de tables: {count}")
        finally:
            db.close()
            
        return True
        
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        print("\n💡 Vérifications à faire:")
        print("   1. PostgreSQL est-il démarré?")
        print("   2. La base de données 'taxe_municipale' existe-t-elle?")
        print("   3. Les credentials dans .env sont-ils corrects?")
        print("   4. Le mot de passe PostgreSQL contient-il des caractères spéciaux?")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)

