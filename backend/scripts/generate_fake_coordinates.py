"""
Script utilitaire pour générer des coordonnées GPS plausibles
pour les quartiers et contribuables dépourvus de géolocalisation.

Usage :
    python scripts/generate_fake_coordinates.py

Options :
    --bounds-file <path>    : fichier JSON contenant les bornes par quartier
    --dry-run               : n'enregistre rien en base (permet de vérifier)
    --force-quartiers       : réécrit les géométries même si elles existent
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path
from typing import Dict, Any

from sqlalchemy import text

# Permet d'exécuter le script depuis n'importe où
CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_ROOT = CURRENT_DIR.parent
PROJECT_ROOT = BACKEND_ROOT.parent
for path in (BACKEND_ROOT, PROJECT_ROOT):
    if str(path) not in sys.path:
        sys.path.append(str(path))

from database.database import SessionLocal

DEFAULT_BOUNDS_PATH = Path(__file__).resolve().parents[1] / "data" / "quartiers_bounds.json"


def load_bounds(path: Path) -> Dict[str, Dict[str, float]]:
    if not path.exists():
        raise FileNotFoundError(f"Fichier de bornes introuvable: {path}")
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    # normaliser les clés (insensibilité à la casse)
    normalized = {k.strip().lower(): v for k, v in data.items()}
    return normalized


def is_valid_coord(lat: Any, lon: Any) -> bool:
    try:
        if lat is None or lon is None:
            return False
        lat = float(lat)
        lon = float(lon)
    except (TypeError, ValueError):
        return False
    if lat == 0 and lon == 0:
        return False
    return -5.0 <= lat <= 5.0 and 6.0 <= lon <= 16.0


def generate_point(bounds: Dict[str, float], seed: int) -> Dict[str, float]:
    rng = random.Random(seed)
    lat = rng.uniform(bounds["lat_min"], bounds["lat_max"])
    lon = rng.uniform(bounds["lon_min"], bounds["lon_max"])
    return {"lat": round(lat, 6), "lon": round(lon, 6)}


def update_quartiers(session, bounds: Dict[str, Dict[str, float]], force: bool) -> int:
    rows = session.execute(text("SELECT id, nom, geom IS NOT NULL AS has_geom FROM quartier")).fetchall()
    updated = 0
    for row in rows:
        name = (row.nom or "").strip().lower()
        if name not in bounds:
            continue
        if row.has_geom and not force:
            continue
        b = bounds[name]
        lat = (b["lat_min"] + b["lat_max"]) / 2
        lon = (b["lon_min"] + b["lon_max"]) / 2
        session.execute(
            text(
                "UPDATE quartier "
                "SET geom = ST_SetSRID(ST_MakePoint(:lon, :lat), 4326) "
                "WHERE id = :id"
            ),
            {"lat": lat, "lon": lon, "id": row.id},
        )
        updated += 1
    return updated


def update_contribuables(session, bounds: Dict[str, Dict[str, float]], force: bool = False) -> int:
    rows = session.execute(
        text(
            "SELECT c.id, c.latitude, c.longitude, q.nom AS quartier "
            "FROM contribuable c "
            "JOIN quartier q ON q.id = c.quartier_id"
        )
    ).fetchall()
    updated = 0
    for row in rows:
        name = (row.quartier or "").strip().lower()
        if name not in bounds:
            continue
        if not force and is_valid_coord(row.latitude, row.longitude):
            continue
        point = generate_point(bounds[name], seed=row.id)
        session.execute(
            text(
                "UPDATE contribuable "
                "SET latitude = :lat, longitude = :lon "
                "WHERE id = :id"
            ),
            {"lat": point["lat"], "lon": point["lon"], "id": row.id},
        )
        updated += 1
    return updated


def main():
    parser = argparse.ArgumentParser(description="Génère des coordonnées factices par quartier.")
    parser.add_argument(
        "--bounds-file",
        type=Path,
        default=DEFAULT_BOUNDS_PATH,
        help="Fichier JSON contenant les bornes géographiques par quartier",
    )
    parser.add_argument("--dry-run", action="store_true", help="Ne pas enregistrer les modifications")
    parser.add_argument(
        "--force-quartiers",
        action="store_true",
        help="Réécrit les géométries des quartiers même si elles existent déjà",
    )
    parser.add_argument(
        "--force-contribuables",
        action="store_true",
        help="Regénère les coordonnées des contribuables même si elles existent déjà",
    )
    args = parser.parse_args()

    bounds = load_bounds(args.bounds_file)
    if not bounds:
        raise ValueError("Le fichier de bornes est vide.")

    session = SessionLocal()
    try:
        q_updated = update_quartiers(session, bounds, force=args.force_quartiers)
        c_updated = update_contribuables(session, bounds, force=args.force_contribuables)

        if args.dry_run:
            session.rollback()
            print(f"[DRY-RUN] Quartiers mis à jour: {q_updated}, Contribuables mis à jour: {c_updated}")
        else:
            session.commit()
            print(f"✅ Quartiers mis à jour: {q_updated}")
            print(f"✅ Contribuables mis à jour: {c_updated}")
    except Exception as exc:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()