"""
Fonctions utilitaires pour calculer les statistiques des collecteurs
"""

from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import func

from database.models import Collecteur, InfoCollecte, StatutCollecteEnum


def compute_statistiques_collecteur(db: Session, collecteur_id: int) -> Optional[dict]:
    """
    Calcule les statistiques principales d'un collecteur à partir des collectes non annulées.
    Retourne un dictionnaire prêt à être converti en réponse API.
    """
    collecteur = db.query(Collecteur).filter(Collecteur.id == collecteur_id).first()
    if not collecteur:
        return None

    base_query = db.query(InfoCollecte).filter(
        InfoCollecte.collecteur_id == collecteur_id,
        InfoCollecte.annule == False  # noqa: E712
    )

    def _sum(field):
        value = base_query.with_entities(func.coalesce(func.sum(field), 0)).scalar()
        return Decimal(value or 0)

    total_collecte = _sum(InfoCollecte.montant)
    commission_totale = _sum(InfoCollecte.commission)

    nombre_collectes = base_query.count()
    collectes_completes = base_query.filter(InfoCollecte.statut == StatutCollecteEnum.COMPLETED).count()
    collectes_en_attente = base_query.filter(InfoCollecte.statut == StatutCollecteEnum.PENDING).count()

    return {
        "collecteur_id": collecteur_id,
        "total_collecte": total_collecte,
        "commission_totale": commission_totale,
        "nombre_collectes": nombre_collectes,
        "collectes_completes": collectes_completes,
        "collectes_en_attente": collectes_en_attente,
    }

