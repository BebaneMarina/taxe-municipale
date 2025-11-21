"""
Script pour corriger le hash de mot de passe de l'utilisateur admin
"""

from database.database import SessionLocal
from database.models import Utilisateur
import bcrypt

def fix_admin_password():
    """Met à jour le hash de mot de passe de l'admin"""
    db = SessionLocal()
    try:
        # Générer un hash valide pour "admin123"
        password = "admin123"
        password_bytes = password.encode('utf-8')
        hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt(rounds=12))
        hash_str = hashed.decode('utf-8')
        
        print(f"Hash généré: {hash_str}")
        
        # Trouver l'utilisateur admin
        admin = db.query(Utilisateur).filter(Utilisateur.email == "admin@mairie-libreville.ga").first()
        
        if admin:
            admin.mot_de_passe_hash = hash_str
            db.commit()
            print("✅ Hash de mot de passe admin mis à jour avec succès!")
        else:
            print("⚠️ Utilisateur admin non trouvé")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    fix_admin_password()

