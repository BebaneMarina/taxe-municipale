"""
Script pour encoder correctement le mot de passe PostgreSQL dans .env
"""

import os
from urllib.parse import quote_plus

def fix_password_in_env():
    """Encode le mot de passe dans le fichier .env"""
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    
    if not os.path.exists(env_path):
        print(f"❌ Fichier .env non trouvé: {env_path}")
        return
    
    print("🔧 Correction de l'encodage du mot de passe PostgreSQL...\n")
    
    try:
        # Lire le fichier avec différents encodages
        content = None
        for encoding in ['utf-8', 'latin-1', 'cp1252']:
            try:
                with open(env_path, 'r', encoding=encoding) as f:
                    content = f.read()
                break
            except:
                continue
        
        if not content:
            print("❌ Impossible de lire le fichier .env")
            return
        
        # Parser et corriger DATABASE_URL
        lines = content.split('\n')
        updated = False
        new_lines = []
        
        for line in lines:
            if line.strip().startswith('DATABASE_URL='):
                # Extraire l'URL
                url = line.split('=', 1)[1].strip()
                
                if url.startswith('postgresql://'):
                    # Parser l'URL
                    try:
                        # Extraire les parties
                        parts = url.replace('postgresql://', '').split('@')
                        if len(parts) == 2:
                            credentials = parts[0]
                            host_db = parts[1]
                            
                            if ':' in credentials:
                                user, password = credentials.split(':', 1)
                                
                                # Encoder le mot de passe
                                password_encoded = quote_plus(password, safe='')
                                
                                # Reconstruire l'URL
                                new_url = f"postgresql://{user}:{password_encoded}@{host_db}"
                                
                                if new_url != url:
                                    new_lines.append(f"DATABASE_URL={new_url}\n")
                                    print(f"✅ Mot de passe encodé avec succès!")
                                    print(f"   Ancienne URL: postgresql://{user}:****@{host_db}")
                                    print(f"   Nouvelle URL: postgresql://{user}:****@{host_db}")
                                    updated = True
                                else:
                                    new_lines.append(line + '\n')
                            else:
                                new_lines.append(line + '\n')
                        else:
                            new_lines.append(line + '\n')
                    except Exception as e:
                        print(f"⚠️ Erreur lors du parsing: {e}")
                        new_lines.append(line + '\n')
                else:
                    new_lines.append(line + '\n')
            else:
                new_lines.append(line + '\n')
        
        # Écrire le fichier corrigé
        if updated:
            with open(env_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            print(f"\n✅ Fichier .env mis à jour avec encodage UTF-8!")
        else:
            print("ℹ️ Aucune modification nécessaire (le mot de passe est déjà encodé ou ne contient pas de caractères spéciaux)")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_password_in_env()
    print("\n💡 Testez maintenant la connexion avec: python -m database.check_connection")

