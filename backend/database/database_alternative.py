"""
Configuration alternative de la base de données avec gestion d'encodage renforcée
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import sys
from urllib.parse import quote_plus, urlparse, urlunparse

# Forcer l'encodage UTF-8 pour Windows
if sys.platform == 'win32':
    import locale
    if sys.getdefaultencoding() != 'utf-8':
        try:
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        except:
            try:
                locale.setlocale(locale.LC_ALL, 'C.UTF-8')
            except:
                pass

def get_database_url():
    """Récupère et encode correctement l'URL de la base de données"""
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    
    # Lire le fichier .env manuellement avec gestion d'erreur
    database_url = None
    if os.path.exists(env_path):
        for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
            try:
                with open(env_path, 'r', encoding=encoding) as f:
                    for line in f:
                        if line.strip().startswith('DATABASE_URL='):
                            database_url = line.split('=', 1)[1].strip()
                            break
                if database_url:
                    break
            except:
                continue
    
    if not database_url:
        database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/taxe_municipale")
    
    # Encoder l'URL si nécessaire
    try:
        if database_url.startswith("postgresql://"):
            parsed = urlparse(database_url)
            if parsed.username and parsed.password:
                # Encoder username et password
                username = quote_plus(parsed.username.encode('utf-8').decode('utf-8'), safe='')
                password = quote_plus(parsed.password.encode('utf-8').decode('utf-8'), safe='')
                
                netloc = f"{username}:{password}@{parsed.hostname}"
                if parsed.port:
                    netloc += f":{parsed.port}"
                
                database_url = urlunparse((
                    parsed.scheme,
                    netloc,
                    parsed.path,
                    parsed.params,
                    parsed.query,
                    parsed.fragment
                ))
    except Exception as e:
        print(f"⚠️ Avertissement encodage URL: {e}")
    
    return database_url

DATABASE_URL = get_database_url()

# Créer le moteur avec gestion d'encodage
try:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        echo=False,
        connect_args={
            "client_encoding": "UTF8",
            "options": "-c client_encoding=UTF8"
        }
    )
except Exception as e:
    print(f"❌ Erreur lors de la création du moteur: {e}")
    raise

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
    Base.metadata.create_all(bind=engine)

