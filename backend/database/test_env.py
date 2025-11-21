"""
Script pour tester et afficher le contenu du fichier .env
"""

import os

def test_env_file():
    """Affiche le contenu du fichier .env"""
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    
    if not os.path.exists(env_path):
        print(f"❌ Fichier .env non trouvé: {env_path}")
        return
    
    print(f"✅ Fichier .env trouvé: {env_path}\n")
    
    try:
        # Essayer différents encodages
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                with open(env_path, 'r', encoding=encoding) as f:
                    content = f.read()
                    print(f"✅ Fichier lisible avec encodage: {encoding}\n")
                    print("Contenu (masqué):")
                    for line in content.split('\n'):
                        if line.strip() and not line.strip().startswith('#'):
                            if 'DATABASE_URL' in line:
                                # Masquer le mot de passe
                                if '://' in line and '@' in line:
                                    parts = line.split('@')
                                    if len(parts) == 2:
                                        creds = parts[0]
                                        if ':' in creds:
                                            user_pass = creds.split(':', 1)
                                            if len(user_pass) == 2:
                                                user = user_pass[0]
                                                password = user_pass[1]
                                                masked = '*' * len(password)
                                                print(f"  DATABASE_URL={user}:{masked}@{parts[1]}")
                                            else:
                                                print(f"  {line[:50]}...")
                                        else:
                                            print(f"  {line[:50]}...")
                                    else:
                                        print(f"  {line[:50]}...")
                                else:
                                    print(f"  {line[:50]}...")
                            else:
                                print(f"  {line}")
                    break
            except UnicodeDecodeError:
                continue
            except Exception as e:
                print(f"❌ Erreur avec encodage {encoding}: {e}")
                continue
        else:
            print("❌ Impossible de lire le fichier avec les encodages testés")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_env_file()

