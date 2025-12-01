"""
Script pour vérifier les noms des quartiers en base de données
et les comparer avec le fichier quartiers_bounds.json
"""

import sys
from pathlib import Path

# Ajouter le chemin du backend au PYTHONPATH
CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_ROOT = CURRENT_DIR.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.append(str(BACKEND_ROOT))

from database.database import SessionLocal
from sqlalchemy import text
import json

def main():
    session = SessionLocal()
    try:
        # Récupérer tous les quartiers
        quartiers = session.execute(
            text("SELECT id, nom, code, geom IS NOT NULL AS has_geom FROM quartier ORDER BY nom")
        ).fetchall()
        
        print(f"\n📊 Total de quartiers en base : {len(quartiers)}\n")
        print("=" * 60)
        print("QUARTIERS EN BASE DE DONNÉES :")
        print("=" * 60)
        
        for q in quartiers:
            geom_status = "✓" if q.has_geom else "✗"
            print(f"{geom_status} ID:{q.id:3d} | {q.nom:30s} | Code: {q.code}")
        
        # Charger le fichier JSON
        json_path = BACKEND_ROOT / "data" / "quartiers_bounds.json"
        if json_path.exists():
            with open(json_path, 'r', encoding='utf-8') as f:
                bounds = json.load(f)
            
            print("\n" + "=" * 60)
            print("QUARTIERS DANS LE FICHIER JSON :")
            print("=" * 60)
            for name in sorted(bounds.keys()):
                print(f"  - {name}")
            
            # Comparer
            print("\n" + "=" * 60)
            print("CORRESPONDANCES :")
            print("=" * 60)
            
            quartiers_lower = {q.nom.strip().lower(): q.nom for q in quartiers}
            bounds_lower = {k.strip().lower(): k for k in bounds.keys()}
            
            matches = []
            missing_in_json = []
            missing_in_db = []
            
            for q_lower, q_original in quartiers_lower.items():
                if q_lower in bounds_lower:
                    matches.append((q_original, bounds_lower[q_lower]))
                else:
                    missing_in_json.append(q_original)
            
            for b_lower, b_original in bounds_lower.items():
                if b_lower not in quartiers_lower:
                    missing_in_db.append(b_original)
            
            if matches:
                print(f"\n✅ {len(matches)} correspondances trouvées :")
                for q_name, b_name in matches:
                    print(f"   '{q_name}' ↔ '{b_name}'")
            
            if missing_in_json:
                print(f"\n⚠️  {len(missing_in_json)} quartiers en base SANS correspondance dans JSON :")
                for name in missing_in_json[:10]:  # Limiter à 10
                    print(f"   - {name}")
                if len(missing_in_json) > 10:
                    print(f"   ... et {len(missing_in_json) - 10} autres")
            
            if missing_in_db:
                print(f"\n⚠️  {len(missing_in_db)} quartiers dans JSON SANS correspondance en base :")
                for name in missing_in_db:
                    print(f"   - {name}")
        else:
            print(f"\n⚠️  Fichier JSON introuvable : {json_path}")
        
    finally:
        session.close()

if __name__ == "__main__":
    main()

