"""
Configuration de la base de données PostgreSQL
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
import sys
from dotenv import load_dotenv
from urllib.parse import quote_plus, urlparse, urlunparse

# Définir l'encodage UTF-8 pour Windows
if sys.platform == 'win32':
    import io
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Charger le fichier .env avec encodage UTF-8
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
if os.path.exists(env_path):
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Parser manuellement pour éviter les problèmes d'encodage
            for line in content.split('\n'):
                if line.strip() and not line.strip().startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
    except Exception as e:
        print(f"⚠️ Erreur lors du chargement du .env: {e}")
        load_dotenv()
else:
    load_dotenv()

# Configuration de la base de données
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:admin@localhost:5432/taxe_municipale"
)

# Encoder correctement l'URL si elle contient des caractères spéciaux
try:
    if DATABASE_URL.startswith("postgresql://"):
        # Parser l'URL pour encoder correctement le mot de passe
        parsed = urlparse(DATABASE_URL)
        if parsed.username and parsed.password:
            # Encoder le username et password
            username_encoded = quote_plus(parsed.username.encode('utf-8').decode('utf-8'))
            password_encoded = quote_plus(parsed.password.encode('utf-8').decode('utf-8'))
            
            # Reconstruire l'URL
            netloc = f"{username_encoded}:{password_encoded}@{parsed.hostname}"
            if parsed.port:
                netloc += f":{parsed.port}"
            
            DATABASE_URL = urlunparse((
                parsed.scheme,
                netloc,
                parsed.path,
                parsed.params,
                parsed.query,
                parsed.fragment
            ))
except Exception as e:
    # Si le parsing échoue, utiliser l'URL telle quelle
    print(f"⚠️ Avertissement: Impossible d'encoder l'URL: {e}")

# Création du moteur SQLAlchemy avec paramètres d'encodage
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Vérifie les connexions avant utilisation
    echo=False,  # Mettre à True pour voir les requêtes SQL
    connect_args={
        "client_encoding": "utf8",
        "options": "-c client_encoding=utf8"
    }
)

# Session locale
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dépendance pour obtenir une session de base de données"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialise la base de données (crée les tables)"""
    from database.models import Base
    
    # Activer PostGIS avant de créer les tables (nécessaire pour les colonnes geometry)
    try:
        with engine.begin() as conn:
            # Activer l'extension PostGIS si elle n'existe pas
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
        print("✅ Extension PostGIS activée ou déjà présente")
    except Exception as e:
        # Si l'activation échoue (droits insuffisants, etc.), on continue quand même
        # car PostGIS pourrait être déjà activé ou les tables pourraient ne pas nécessiter PostGIS
        print(f"⚠️ Avertissement: Impossible d'activer PostGIS automatiquement: {e}")
        print("   Si vous avez des colonnes geometry, vous devrez activer PostGIS manuellement:")
        print("   CREATE EXTENSION IF NOT EXISTS postgis;")
    
    # Créer les tables
    Base.metadata.create_all(bind=engine)

