"""
Script pour corriger les problèmes d'encodage dans la connexion PostgreSQL
"""

import os
from urllib.parse import quote_plus, urlparse, parse_qs, urlencode, urlunparse

def fix_database_url(url):
    """Corrige l'URL de la base de données pour éviter les problèmes d'encodage"""
    if not url:
        return url
    
    try:
        # Parser l'URL
        parsed = urlparse(url)
        
        # Extraire les credentials
        if parsed.username and parsed.password:
            # Encoder le mot de passe
            username = quote_plus(parsed.username)
            password = quote_plus(parsed.password)
            
            # Reconstruire l'URL
            netloc = f"{username}:{password}@{parsed.hostname}"
            if parsed.port:
                netloc += f":{parsed.port}"
            
            # Reconstruire l'URL complète
            fixed_url = urlunparse((
                parsed.scheme,
                netloc,
                parsed.path,
                parsed.params,
                parsed.query,
                parsed.fragment
            ))
            
            return fixed_url
    except Exception as e:
        print(f"⚠️ Erreur lors de la correction de l'URL: {e}")
        return url
    
    return url

def update_env_file():
    """Met à jour le fichier .env avec l'URL corrigée"""
    # Chercher le fichier .env dans le dossier backend (parent de database)
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(backend_dir, '.env')
    
    # Essayer aussi le chemin relatif
    if not os.path.exists(env_path):
        env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
        env_path = os.path.abspath(env_path)
    
    if not os.path.exists(env_path):
        print(f"⚠️ Fichier .env non trouvé: {env_path}")
        print(f"💡 Cherchez le fichier .env dans le dossier backend/")
        return
    
    try:
        # Lire le fichier .env
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Modifier la ligne DATABASE_URL
        updated = False
        new_lines = []
        for line in lines:
            if line.startswith('DATABASE_URL='):
                old_url = line.split('=', 1)[1].strip()
                new_url = fix_database_url(old_url)
                if new_url != old_url:
                    new_lines.append(f"DATABASE_URL={new_url}\n")
                    print(f"✅ URL corrigée:")
                    print(f"   Ancienne: {old_url[:50]}...")
                    print(f"   Nouvelle: {new_url[:50]}...")
                    updated = True
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
        
        # Écrire le fichier mis à jour
        if updated:
            with open(env_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            print(f"\n✅ Fichier .env mis à jour!")
        else:
            print("ℹ️ Aucune modification nécessaire")
            
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour: {e}")

if __name__ == "__main__":
    print("🔧 Correction des problèmes d'encodage...")
    update_env_file()
    print("\n💡 Si le problème persiste:")
    print("   1. Vérifiez que votre mot de passe PostgreSQL ne contient pas de caractères spéciaux")
    print("   2. Ou encodez-le manuellement dans le fichier .env")
    print("   3. Exemple: postgresql://user:mot%40passe@localhost:5432/db")

