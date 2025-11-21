"""
Script pour mettre à jour le fichier .env avec le bon mot de passe
"""

import os

def update_env_file():
    """Met à jour le fichier .env avec le mot de passe 'admin'"""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    
    if not os.path.exists(env_path):
        print(f"❌ Fichier .env non trouvé: {env_path}")
        return
    
    # Contenu du fichier .env avec mot de passe 'admin'
    content = """# Configuration de la base de données PostgreSQL
# Modifiez les valeurs selon votre configuration
DATABASE_URL=postgresql://postgres:admin@localhost:5432/taxe_municipale

# Configuration de l'application
ENVIRONMENT=development
DEBUG=True

# Configuration JWT (optionnel)
# SECRET_KEY=votre-secret-key-tres-securisee-changez-moi-en-production
"""
    
    try:
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Fichier .env mis à jour avec le mot de passe 'admin'")
        print(f"   DATABASE_URL=postgresql://postgres:admin@localhost:5432/taxe_municipale")
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour: {e}")

if __name__ == "__main__":
    update_env_file()

