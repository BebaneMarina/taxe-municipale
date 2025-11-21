"""
Seeder pour créer un utilisateur admin par défaut
"""

from sqlalchemy.orm import Session
from database.models import Utilisateur, RoleEnum
from auth.security import get_password_hash


def seed_admin_user(db: Session):
    """Crée un utilisateur admin par défaut"""
    admin_email = "admin@mairie-libreville.ga"
    admin = db.query(Utilisateur).filter(Utilisateur.email == admin_email).first()
    
    if not admin:
        admin = Utilisateur(
            nom="Admin",
            prenom="Système",
            email=admin_email,
            telephone="+241062345678",
            mot_de_passe_hash=get_password_hash("admin123"),  # À changer en production !
            role=RoleEnum.ADMIN,
            actif=True
        )
        db.add(admin)
        db.commit()
        print("✅ Utilisateur admin créé (email: admin@mairie-libreville.ga, password: admin123)")
    else:
        print("ℹ️ Utilisateur admin existe déjà")


if __name__ == "__main__":
    from database.database import SessionLocal
    
    db = SessionLocal()
    try:
        seed_admin_user(db)
    finally:
        db.close()

