"""
Routes dédiées aux statistiques pour l'application mobile
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from auth.security import get_current_active_user
from database.database import get_db
from schemas.statistiques_collecteur import StatistiquesCollecteurResponse
from services.statistiques_collecteur import compute_statistiques_collecteur

router = APIRouter(
    prefix="/api/statistiques",
    tags=["statistiques"],
    dependencies=[Depends(get_current_active_user)],
)


@router.get("/collecteur/{collecteur_id}", response_model=StatistiquesCollecteurResponse)
def get_statistiques_collecteur_route(
    collecteur_id: int,
    db: Session = Depends(get_db),
):
    """Expose les statistiques d'un collecteur via /api/statistiques/collecteur/{collecteur_id}"""
    stats = compute_statistiques_collecteur(db, collecteur_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Collecteur non trouvé")
    return stats

