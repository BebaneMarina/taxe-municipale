"""
Endpoints pour les préférences d'accessibilité et l'application mobile
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from auth.security import get_current_active_user
from database.database import get_db
from database.models import PreferenceUtilisateur, Utilisateur
from schemas.preferences import (
    PreferencesDefaultsResponse,
    PreferencesUpdateRequest,
    PreferencesUpdateResponse,
)

router = APIRouter(prefix="/api/app", tags=["application"])


DEFAULT_PREFERENCES = PreferencesDefaultsResponse(
    theme_defaut="systeme",
    mode_sombre_disponible=True,
    contrastes_disponibles=["normal", "eleve"],
    tailles_police=["petit", "moyen", "grand"],
    animations_autorisees=True,
    sons_confirmation=True,
)


@router.get("/preferences", response_model=PreferencesDefaultsResponse)
def get_default_preferences(
    current_user: Utilisateur = Depends(get_current_active_user),
):
    """
    Retourne les préférences serveur par défaut pour l'accessibilité.
    L'utilisateur courant est vérifié mais la réponse reflète les valeurs globales.
    """
    return DEFAULT_PREFERENCES


@router.patch("/preferences", response_model=PreferencesUpdateResponse)
def update_preferences(
    payload: PreferencesUpdateRequest,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_active_user),
):
    """
    Sauvegarde les préférences du collecteur / utilisateur connecté.
    """
    if not payload.model_dump(exclude_unset=True):
        raise HTTPException(status_code=400, detail="Aucune donnée fournie")

    prefs = (
        db.query(PreferenceUtilisateur)
        .filter(PreferenceUtilisateur.user_id == current_user.id)
        .first()
    )

    if not prefs:
        prefs = PreferenceUtilisateur(
            user_id=current_user.id,
            theme=payload.theme or DEFAULT_PREFERENCES.theme_defaut,
            contraste=payload.contraste or DEFAULT_PREFERENCES.contrastes_disponibles[0],
            taille_police=payload.taille_police or DEFAULT_PREFERENCES.tailles_police[1],
            animations=payload.animations
            if payload.animations is not None
            else DEFAULT_PREFERENCES.animations_autorisees,
            sons=payload.sons
            if payload.sons is not None
            else DEFAULT_PREFERENCES.sons_confirmation,
            lang=payload.lang or "fr",
        )
        db.add(prefs)
    else:
        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(prefs, field, value)

    db.commit()
    db.refresh(prefs)

    return PreferencesUpdateResponse(
        user_id=prefs.user_id,
        collecteur_id=prefs.collecteur_id,
        theme=prefs.theme,
        contraste=prefs.contraste,
        taille_police=prefs.taille_police,
        animations=prefs.animations,
        sons=prefs.sons,
        lang=prefs.lang,
    )

