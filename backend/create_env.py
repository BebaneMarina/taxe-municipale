"""
Script pour créer le fichier .env si il n'existe pas
"""

import os
from pathlib import Path

def create_env_file():
    """Crée le fichier .env avec la configuration par défaut"""
    env_path = Path(__file__).parent / '.env'
    
    if env_path.exists():
        print(f"ℹ️ Le fichier .env existe déjà: {env_path}")
        return
    
    env_content = """# Configuration de la base de données PostgreSQL
# Modifiez les valeurs selon votre configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/taxe_municipale

# Configuration de l'application
ENVIRONMENT=development
DEBUG=True

# Configuration JWT (optionnel)
# SECRET_KEY=votre-secret-key-tres-securisee-changez-moi-en-production
"""
    
    try:
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(env_content)
        print(f"✅ Fichier .env créé: {env_path}")
        print("\n📝 Veuillez modifier DATABASE_URL avec vos credentials PostgreSQL")
        print("   Format: postgresql://utilisateur:mot_de_passe@localhost:5432/taxe_municipale")
        print("\n💡 Si votre mot de passe contient des caractères spéciaux, encodez-les:")
        print("   @ → %40")
        print("   # → %23")
        print("   % → %25")
    except Exception as e:
        print(f"❌ Erreur lors de la création du fichier .env: {e}")

if __name__ == "__main__":
    create_env_file()

