"""
Script pour générer des coordonnées GPS pour TOUS les quartiers
même ceux qui n'ont pas de correspondance dans quartiers_bounds.json
"""

import sys
import random
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_ROOT = CURRENT_DIR.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.append(str(BACKEND_ROOT))

from database.database import SessionLocal
from sqlalchemy import text

# Zone par défaut pour Libreville (si pas de correspondance dans JSON)
LIBREVILLE_BOUNDS = {
    "lat_min": 0.30,
    "lat_max": 0.50,
    "lon_min": 9.40,
    "lon_max": 9.60
}

def generate_point_in_bounds(bounds, seed=None):
    """Génère un point aléatoire dans les bornes données"""
    if seed is not None:
        random.seed(seed)
    lat = random.uniform(bounds["lat_min"], bounds["lat_max"])
    lon = random.uniform(bounds["lon_min"], bounds["lon_max"])
    return {"lat": round(lat, 6), "lon": round(lon, 6)}

def update_all_quartiers(session, force=False):
    """Met à jour tous les quartiers avec des coordonnées"""
    quartiers = session.execute(
        text("SELECT id, nom, geom IS NOT NULL AS has_geom FROM quartier ORDER BY nom")
    ).fetchall()
    
    updated = 0
    for q in quartiers:
        if q.has_geom and not force:
            continue
        
        # Générer des coordonnées dans la zone de Libreville
        point = generate_point_in_bounds(LIBREVILLE_BOUNDS, seed=q.id)
        
        # Mettre à jour la colonne geom
        session.execute(
            text(
                "UPDATE quartier "
                "SET geom = ST_SetSRID(ST_MakePoint(:lon, :lat), 4326) "
                "WHERE id = :id"
            ),
            {"lat": point["lat"], "lon": point["lon"], "id": q.id}
        )
        updated += 1
    
    return updated

def update_contribuables_without_coords(session, force=False):
    """Met à jour les contribuables sans coordonnées valides"""
    contribuables = session.execute(
        text(
            "SELECT c.id, c.latitude, c.longitude, q.geom AS quartier_geom "
            "FROM contribuable c "
            "JOIN quartier q ON q.id = c.quartier_id "
            "WHERE (c.latitude IS NULL OR c.longitude IS NULL "
            "   OR c.latitude = 0 OR c.longitude = 0 "
            "   OR c.latitude NOT BETWEEN -5 AND 5 "
            "   OR c.longitude NOT BETWEEN 6 AND 16)"
        )
    ).fetchall()
    
    updated = 0
    for c in contribuables:
        if not force and c.latitude and c.longitude:
            if -5 <= float(c.latitude) <= 5 and 6 <= float(c.longitude) <= 16:
                continue
        
        # Utiliser la géométrie du quartier si disponible
        if c.quartier_geom:
            point = {
                "lat": round(float(c.quartier_geom.y), 6),
                "lon": round(float(c.quartier_geom.x), 6)
            }
            # Ajouter un petit décalage aléatoire pour éviter que tous les contribuables
            # du même quartier soient au même endroit
            offset_lat = random.uniform(-0.005, 0.005)
            offset_lon = random.uniform(-0.005, 0.005)
            point["lat"] += offset_lat
            point["lon"] += offset_lon
        else:
            # Sinon, utiliser la zone par défaut
            point = generate_point_in_bounds(LIBREVILLE_BOUNDS, seed=c.id)
        
        session.execute(
            text(
                "UPDATE contribuable "
                "SET latitude = :lat, longitude = :lon "
                "WHERE id = :id"
            ),
            {"lat": point["lat"], "lon": point["lon"], "id": c.id}
        )
        updated += 1
    
    return updated

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Génère des coordonnées pour tous les quartiers et contribuables")
    parser.add_argument("--force-quartiers", action="store_true", help="Force la mise à jour même si geom existe")
    parser.add_argument("--force-contribuables", action="store_true", help="Force la mise à jour même si coordonnées existent")
    parser.add_argument("--dry-run", action="store_true", help="Ne pas enregistrer les modifications")
    args = parser.parse_args()
    
    session = SessionLocal()
    try:
        q_updated = update_all_quartiers(session, force=args.force_quartiers)
        c_updated = update_contribuables_without_coords(session, force=args.force_contribuables)
        
        if args.dry_run:
            session.rollback()
            print(f"[DRY-RUN] Quartiers à mettre à jour: {q_updated}")
            print(f"[DRY-RUN] Contribuables à mettre à jour: {c_updated}")
        else:
            session.commit()
            print(f"✅ {q_updated} quartiers mis à jour avec des coordonnées")
            print(f"✅ {c_updated} contribuables mis à jour avec des coordonnées")
    except Exception as e:
        session.rollback()
        print(f"❌ Erreur: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    main()

