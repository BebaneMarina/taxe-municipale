"""
Script pour importer les données du dump SQL (dump_taxe.sql)
Ce script permet d'importer les données gabonaises réelles dans la base de données
"""

import os
import sys
import subprocess
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.database import DATABASE_URL, engine
from sqlalchemy import text
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def import_dump_sql(dump_file_path: str = None, database_url: str = None):
    """
    Importe un dump SQL dans la base de données PostgreSQL
    
    Args:
        dump_file_path: Chemin vers le fichier dump SQL (par défaut: backend/dump_taxe.sql)
        database_url: URL de connexion à la base de données
    """
    if dump_file_path is None:
        # Chemin par défaut
        dump_file_path = Path(__file__).parent.parent / "dump_taxe.sql"
    
    if database_url is None:
        database_url = DATABASE_URL
    
    if not os.path.exists(dump_file_path):
        print(f"❌ Erreur: Le fichier {dump_file_path} n'existe pas")
        return False
    
    print(f"📂 Fichier dump trouvé: {dump_file_path}")
    print(f"📊 Taille du fichier: {os.path.getsize(dump_file_path) / 1024 / 1024:.2f} MB")
    
    # Parser l'URL de la base de données
    from urllib.parse import urlparse
    parsed = urlparse(database_url)
    
    db_name = parsed.path.lstrip('/')
    db_user = parsed.username or 'postgres'
    db_password = parsed.password or ''
    db_host = parsed.hostname or 'localhost'
    db_port = parsed.port or 5432
    
    print(f"\n🔌 Connexion à la base de données:")
    print(f"   - Host: {db_host}")
    print(f"   - Port: {db_port}")
    print(f"   - Database: {db_name}")
    print(f"   - User: {db_user}")
    
    try:
        # Méthode 1: Utiliser psql directement (plus rapide et fiable)
        print("\n📥 Importation du dump SQL avec psql...")
        
        # Construire la commande psql
        env = os.environ.copy()
        if db_password:
            env['PGPASSWORD'] = db_password
        
        cmd = [
            'psql',
            '-h', db_host,
            '-p', str(db_port),
            '-U', db_user,
            '-d', db_name,
            '-f', str(dump_file_path)
        ]
        
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if result.returncode == 0:
            print("✅ Importation réussie avec psql!")
            return True
        else:
            print(f"⚠️ Erreur avec psql: {result.stderr}")
            print("🔄 Tentative avec Python...")
            
            # Méthode 2: Utiliser Python pour lire et exécuter le fichier
            return import_with_python(dump_file_path, database_url)
            
    except FileNotFoundError:
        print("⚠️ psql n'est pas trouvé dans le PATH")
        print("🔄 Utilisation de la méthode Python...")
        return import_with_python(dump_file_path, database_url)
    except Exception as e:
        print(f"❌ Erreur lors de l'importation: {e}")
        return False


def import_with_python(dump_file_path: str, database_url: str):
    """
    Importe le dump SQL en utilisant Python (plus lent mais plus portable)
    """
    try:
        from urllib.parse import urlparse
        parsed = urlparse(database_url)
        
        db_name = parsed.path.lstrip('/')
        db_user = parsed.username or 'postgres'
        db_password = parsed.password or ''
        db_host = parsed.hostname or 'localhost'
        db_port = parsed.port or 5432
        
        # Connexion à la base de données
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("📖 Lecture du fichier dump...")
        
        # Lire le fichier dump
        with open(dump_file_path, 'r', encoding='utf-8') as f:
            dump_content = f.read()
        
        # Diviser en commandes SQL (séparées par ;)
        # Note: Cette méthode est simplifiée et peut ne pas gérer tous les cas
        # Pour un dump complet, il vaut mieux utiliser psql
        
        # Exécuter le dump par blocs
        print("⚙️ Exécution des commandes SQL...")
        
        # Pour les gros fichiers, on peut utiliser execute avec le contenu complet
        # mais cela peut être problématique pour les très gros fichiers
        try:
            cursor.execute(dump_content)
            print("✅ Importation réussie avec Python!")
            return True
        except Exception as e:
            print(f"⚠️ Erreur lors de l'exécution: {e}")
            print("💡 Conseil: Utilisez psql directement pour de meilleures performances")
            print(f"   Commande: psql -h {db_host} -U {db_user} -d {db_name} -f {dump_file_path}")
            return False
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erreur lors de l'importation avec Python: {e}")
        return False


def verify_import():
    """
    Vérifie que les données ont été importées correctement
    """
    from database.database import SessionLocal
    from database.models import Contribuable, Collecteur, Taxe, InfoCollecte
    
    db = SessionLocal()
    
    try:
        print("\n🔍 Vérification des données importées...")
        
        # Compter les enregistrements
        nb_contribuables = db.query(Contribuable).count()
        nb_collecteurs = db.query(Collecteur).count()
        nb_taxes = db.query(Taxe).count()
        nb_collectes = db.query(InfoCollecte).count()
        
        print(f"   ✅ Contribuables: {nb_contribuables}")
        print(f"   ✅ Collecteurs: {nb_collecteurs}")
        print(f"   ✅ Taxes: {nb_taxes}")
        print(f"   ✅ Collectes: {nb_collectes}")
        
        # Vérifier les coordonnées GPS
        contribuables_avec_gps = db.query(Contribuable).filter(
            Contribuable.latitude.isnot(None),
            Contribuable.longitude.isnot(None)
        ).count()
        
        print(f"   ✅ Contribuables avec GPS: {contribuables_avec_gps}")
        
        if nb_contribuables > 0:
            print("\n✅ Importation vérifiée avec succès!")
            return True
        else:
            print("\n⚠️ Aucune donnée trouvée. L'importation a peut-être échoué.")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Importer les données du dump SQL")
    parser.add_argument(
        "--dump-file",
        type=str,
        help="Chemin vers le fichier dump SQL (défaut: backend/dump_taxe.sql)"
    )
    parser.add_argument(
        "--database-url",
        type=str,
        help="URL de connexion à la base de données"
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Vérifier uniquement les données importées sans importer"
    )
    
    args = parser.parse_args()
    
    if args.verify_only:
        verify_import()
    else:
        print("🚀 Démarrage de l'importation du dump SQL...\n")
        
        success = import_dump_sql(
            dump_file_path=args.dump_file,
            database_url=args.database_url
        )
        
        if success:
            verify_import()
        else:
            print("\n❌ L'importation a échoué. Vérifiez les erreurs ci-dessus.")
            sys.exit(1)

