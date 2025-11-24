"""
Endpoints pour la localisation / traduction de l'application mobile
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from database.database import get_db
from database.models import LangueDisponible, TexteLocalisation
from schemas.localisation import (
    LanguesDisponiblesResponse,
    LangueDisponibleItem,
    TexteLocalisationResponse,
)

router = APIRouter(prefix="/api/localisation", tags=["localisation"])

FALLBACK_LANG = {
    "code": "fr",
    "nom": "Français",
    "direction": "ltr",
    "defaut": True,
    "version": 1,
    "strings": {
        "app.title": "E-Taxe",
        "dashboard.collectes": "Collectes",
        "dashboard.contribuables": "Contribuables",
    },
}


@router.get("/textes", response_model=TexteLocalisationResponse)
def get_textes_localises(
    lang: str = Query("fr", min_length=2, max_length=10),
    version: int | None = Query(None),
    db: Session = Depends(get_db),
):
    """
    Retourne les libellés à jour pour la langue demandée.
    """
    langue = (
        db.query(LangueDisponible)
        .filter(LangueDisponible.code == lang, LangueDisponible.active == True)
        .first()
    )

    if not langue:
        if lang != FALLBACK_LANG["code"]:
            raise HTTPException(status_code=404, detail="Langue non disponible")
        return TexteLocalisationResponse(
            lang=FALLBACK_LANG["code"],
            version=FALLBACK_LANG["version"],
            strings=FALLBACK_LANG["strings"],
        )

    query = (
        db.query(TexteLocalisation)
        .filter(TexteLocalisation.langue_id == langue.id, TexteLocalisation.actif == True)
        .order_by(desc(TexteLocalisation.version))
    )

    if version:
        texte = query.filter(TexteLocalisation.version == version).first()
    else:
        texte = query.first()

    if not texte:
        return TexteLocalisationResponse(
            lang=langue.code,
            version=langue.version,
            strings=FALLBACK_LANG["strings"],
        )

    return TexteLocalisationResponse(
        lang=langue.code,
        version=texte.version,
        strings=texte.strings or {},
    )


@router.get("/disponibles", response_model=LanguesDisponiblesResponse)
def get_langues_disponibles(db: Session = Depends(get_db)):
    """
    Retourne la liste des langues activées pour l'app mobile.
    """
    langues = (
        db.query(LangueDisponible)
        .filter(LangueDisponible.active == True)
        .order_by(LangueDisponible.nom.asc())
        .all()
    )

    if not langues:
        return LanguesDisponiblesResponse(
            langues=[
                LangueDisponibleItem(
                    code=FALLBACK_LANG["code"],
                    nom=FALLBACK_LANG["nom"],
                    direction=FALLBACK_LANG["direction"],
                    defaut=FALLBACK_LANG["defaut"],
                    version=FALLBACK_LANG["version"],
                )
            ]
        )

    return LanguesDisponiblesResponse(
        langues=[
            LangueDisponibleItem(
                code=langue.code,
                nom=langue.nom,
                direction=langue.direction,
                defaut=langue.defaut,
                version=langue.version,
            )
            for langue in langues
        ]
    )

