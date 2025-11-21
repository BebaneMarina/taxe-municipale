"""
Script pour générer des hash de mots de passe valides
"""

import bcrypt

def generate_hash(password: str) -> str:
    """Génère un hash bcrypt pour un mot de passe"""
    password_bytes = password.encode('utf-8')
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt(rounds=12))
    return hashed.decode('utf-8')

if __name__ == "__main__":
    print("Hash pour 'admin123':")
    print(generate_hash("admin123"))
    print("\nHash pour 'password123':")
    print(generate_hash("password123"))

