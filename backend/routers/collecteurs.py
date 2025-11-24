"""
Routes pour la gestion des collecteurs
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import List, Optional
from database.database import get_db
from database.models import (
    Collecteur,
    StatutCollecteurEnum,
    EtatCollecteurEnum,
    InfoCollecte,
    StatutCollecteEnum,
    ObjectifCollecteur,
    PerformanceCollecteur,
    BadgeCollecteur,
    BadgeFeedback,
)
from schemas.collecteur import CollecteurCreate, CollecteurUpdate, CollecteurResponse
from schemas.activite_collecteur import ActiviteCollecteurResponse, ActiviteJour
from schemas.statistiques_collecteur import StatistiquesCollecteurResponse
from services.statistiques_collecteur import compute_statistiques_collecteur
from auth.security import get_current_active_user
from schemas.performances import (
    ObjectifsCollecteurResponse,
    PerformancesResponse,
    PerformancePoint,
    BadgesResponse,
    BadgeItem,
    FeedbackRequest,
)
from datetime import datetime, timedelta
from decimal import Decimal

router = APIRouter(
    prefix="/api/collecteurs",
    tags=["collecteurs"],
    dependencies=[Depends(get_current_active_user)],
)


def _ensure_collecteur(db: Session, collecteur_id: int) -> Collecteur:
    collecteur = db.query(Collecteur).filter(Collecteur.id == collecteur_id).first()
    if not collecteur:
        raise HTTPException(status_code=404, detail="Collecteur non trouvé")
    return collecteur


def make_point(longitude: Optional[float], latitude: Optional[float]):
    if longitude is None or latitude is None:
        return None
    return func.ST_SetSRID(func.ST_MakePoint(longitude, latitude), 4326)


@router.get("/", response_model=List[CollecteurResponse])
def get_collecteurs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    statut: Optional[str] = None,
    etat: Optional[str] = None,
    zone_id: Optional[int] = None,
    actif: Optional[bool] = None,
    search: Optional[str] = None,
    email: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Récupère la liste des collecteurs avec filtres"""
    query = db.query(Collecteur)
    
    if actif is not None:
        query = query.filter(Collecteur.actif == actif)
    if statut:
        try:
            statut_enum = StatutCollecteurEnum(statut)
            query = query.filter(Collecteur.statut == statut_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail="Statut invalide")
    if etat:
        try:
            etat_enum = EtatCollecteurEnum(etat)
            query = query.filter(Collecteur.etat == etat_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail="État invalide")
    if zone_id:
        query = query.filter(Collecteur.zone_id == zone_id)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Collecteur.nom.ilike(search_term)) |
            (Collecteur.prenom.ilike(search_term)) |
            (Collecteur.matricule.ilike(search_term)) |
            (Collecteur.email.ilike(search_term))
        )
    if email:
        query = query.filter(func.lower(Collecteur.email) == email.lower())
    
    collecteurs = query.offset(skip).limit(limit).all()
    return collecteurs


@router.get("/{collecteur_id}", response_model=CollecteurResponse)
def get_collecteur(collecteur_id: int, db: Session = Depends(get_db)):
    """Récupère un collecteur par son ID"""
    collecteur = db.query(Collecteur).filter(Collecteur.id == collecteur_id).first()
    if not collecteur:
        raise HTTPException(status_code=404, detail="Collecteur non trouvé")
    return collecteur


@router.post("/", response_model=CollecteurResponse, status_code=201)
def create_collecteur(collecteur: CollecteurCreate, db: Session = Depends(get_db)):
    """Crée un nouveau collecteur"""
    # Vérifier si le matricule existe déjà
    existing = db.query(Collecteur).filter(Collecteur.matricule == collecteur.matricule).first()
    if existing:
        raise HTTPException(status_code=400, detail="Un collecteur avec ce matricule existe déjà")
    
    # Vérifier si l'email existe déjà
    existing_email = db.query(Collecteur).filter(Collecteur.email == collecteur.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Un collecteur avec cet email existe déjà")
    
    db_collecteur = Collecteur(
        **collecteur.dict(),
        statut=StatutCollecteurEnum.ACTIVE,
        etat=EtatCollecteurEnum.DECONNECTE
    )
    db.add(db_collecteur)
    db.commit()
    db.refresh(db_collecteur)
    return db_collecteur


@router.put("/{collecteur_id}", response_model=CollecteurResponse)
@router.patch("/{collecteur_id}", response_model=CollecteurResponse)
def update_collecteur(collecteur_id: int, collecteur_update: CollecteurUpdate, db: Session = Depends(get_db)):
    """Met à jour un collecteur"""
    db_collecteur = db.query(Collecteur).filter(Collecteur.id == collecteur_id).first()
    if not db_collecteur:
        raise HTTPException(status_code=404, detail="Collecteur non trouvé")
    
    update_data = collecteur_update.dict(exclude_unset=True)
    
    # Gérer le statut
    if "statut" in update_data:
        try:
            update_data["statut"] = StatutCollecteurEnum(update_data["statut"])
        except ValueError:
            raise HTTPException(status_code=400, detail="Statut invalide")
    
    for field, value in update_data.items():
        setattr(db_collecteur, field, value)
    
    if "latitude" in update_data or "longitude" in update_data:
        geom_point = make_point(db_collecteur.longitude, db_collecteur.latitude)
        db_collecteur.geom = geom_point
    
    db_collecteur.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_collecteur)
    return db_collecteur


@router.get("/{collecteur_id}/statistiques", response_model=StatistiquesCollecteurResponse)
def get_collecteur_statistiques(collecteur_id: int, db: Session = Depends(get_db)):
    """Expose les statistiques nécessaires à l'application mobile"""
    stats = compute_statistiques_collecteur(db, collecteur_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Collecteur non trouvé")
    return stats


def _objectifs_response(
    collecteur_id: int,
    objectifs: ObjectifCollecteur | None,
) -> ObjectifsCollecteurResponse:
    if objectifs:
        return ObjectifsCollecteurResponse(
            collecteur_id=collecteur_id,
            objectif_journalier=objectifs.objectif_journalier or Decimal("0"),
            objectif_hebdo=objectifs.objectif_hebdo or Decimal("0"),
            objectif_mensuel=objectifs.objectif_mensuel or Decimal("0"),
            devise=objectifs.devise or "XAF",
            periode_courante=objectifs.periode_courante or "jour",
        )
    return ObjectifsCollecteurResponse(
        collecteur_id=collecteur_id,
        objectif_journalier=Decimal("0"),
        objectif_hebdo=Decimal("0"),
        objectif_mensuel=Decimal("0"),
        devise="XAF",
        periode_courante="jour",
    )


def _fallback_performances(
    db: Session,
    collecteur_id: int,
    periode: str,
) -> list[PerformancePoint]:
    from datetime import timedelta

    today = datetime.utcnow().date()
    points: list[PerformancePoint] = []

    if periode == "jour":
        span = 7
        for idx in range(span):
            day = today - timedelta(days=span - idx - 1)
            montant = db.query(func.coalesce(func.sum(InfoCollecte.montant), 0)).filter(
                InfoCollecte.collecteur_id == collecteur_id,
                InfoCollecte.annule == False,
                func.date(InfoCollecte.date_collecte) == day,
            ).scalar() or Decimal("0")
            nombre = db.query(func.count(InfoCollecte.id)).filter(
                InfoCollecte.collecteur_id == collecteur_id,
                InfoCollecte.annule == False,
                func.date(InfoCollecte.date_collecte) == day,
            ).scalar() or 0
            points.append(
                PerformancePoint(
                    label=day.strftime("%d/%m"),
                    date_debut=datetime.combine(day, datetime.min.time()),
                    date_fin=datetime.combine(day, datetime.max.time()),
                    montant=Decimal(montant),
                    nombre_collectes=nombre,
                )
            )
    elif periode == "semaine":
        span = 4
        for idx in range(span):
            start = today - timedelta(days=(span - idx) * 7)
            end = start + timedelta(days=6)
            montant = db.query(func.coalesce(func.sum(InfoCollecte.montant), 0)).filter(
                InfoCollecte.collecteur_id == collecteur_id,
                InfoCollecte.annule == False,
                func.date(InfoCollecte.date_collecte) >= start,
                func.date(InfoCollecte.date_collecte) <= end,
            ).scalar() or Decimal("0")
            nombre = db.query(func.count(InfoCollecte.id)).filter(
                InfoCollecte.collecteur_id == collecteur_id,
                InfoCollecte.annule == False,
                func.date(InfoCollecte.date_collecte) >= start,
                func.date(InfoCollecte.date_collecte) <= end,
            ).scalar() or 0
            points.append(
                PerformancePoint(
                    label=f"S{idx + 1}",
                    date_debut=datetime.combine(start, datetime.min.time()),
                    date_fin=datetime.combine(end, datetime.max.time()),
                    montant=Decimal(montant),
                    nombre_collectes=nombre,
                )
            )
    else:  # mois
        span = 6
        ref_month = today.replace(day=1)
        for idx in range(span):
            month_start = (ref_month - timedelta(days=idx * 30)).replace(day=1)
            next_month = (month_start + timedelta(days=32)).replace(day=1)
            month_end = next_month - timedelta(seconds=1)
            montant = db.query(func.coalesce(func.sum(InfoCollecte.montant), 0)).filter(
                InfoCollecte.collecteur_id == collecteur_id,
                InfoCollecte.annule == False,
                InfoCollecte.date_collecte >= datetime.combine(
                    month_start, datetime.min.time()
                ),
                InfoCollecte.date_collecte <= month_end,
            ).scalar() or Decimal("0")
            nombre = db.query(func.count(InfoCollecte.id)).filter(
                InfoCollecte.collecteur_id == collecteur_id,
                InfoCollecte.annule == False,
                InfoCollecte.date_collecte >= datetime.combine(
                    month_start, datetime.min.time()
                ),
                InfoCollecte.date_collecte <= month_end,
            ).scalar() or 0
            points.append(
                PerformancePoint(
                    label=month_start.strftime("%m/%Y"),
                    date_debut=datetime.combine(month_start, datetime.min.time()),
                    date_fin=month_end,
                    montant=Decimal(montant),
                    nombre_collectes=nombre,
                )
            )
        points.reverse()
    return points


@router.get("/{collecteur_id}/objectifs", response_model=ObjectifsCollecteurResponse)
def get_collecteur_objectifs(
    collecteur_id: int,
    db: Session = Depends(get_db),
):
    """Retourne les objectifs assignés au collecteur"""
    _ensure_collecteur(db, collecteur_id)
    objectifs = (
        db.query(ObjectifCollecteur)
        .filter(ObjectifCollecteur.collecteur_id == collecteur_id)
        .first()
    )
    return _objectifs_response(collecteur_id, objectifs)


@router.get("/{collecteur_id}/performances", response_model=PerformancesResponse)
def get_collecteur_performances(
    collecteur_id: int,
    periode: str = Query("jour", pattern="^(jour|semaine|mois)$"),
    db: Session = Depends(get_db),
):
    """Historique des montants/volumes pour alimenter les graphiques"""
    _ensure_collecteur(db, collecteur_id)
    points_db = (
        db.query(PerformanceCollecteur)
        .filter(
            PerformanceCollecteur.collecteur_id == collecteur_id,
            PerformanceCollecteur.periode == periode,
        )
        .order_by(PerformanceCollecteur.date_debut.asc())
        .all()
    )

    if points_db:
        points = [
            PerformancePoint(
                label=p.label,
                date_debut=p.date_debut,
                date_fin=p.date_fin,
                montant=p.montant or Decimal("0"),
                nombre_collectes=p.nombre_collectes or 0,
            )
            for p in points_db
        ]
        progression = points_db[-1].progression_vs_objectif or Decimal("0")
    else:
        points = _fallback_performances(db, collecteur_id, periode)
        progression = Decimal("0")

    return PerformancesResponse(
        periode=periode,
        points=points,
        progression_vs_objectif=progression,
    )


@router.get("/{collecteur_id}/badges", response_model=BadgesResponse)
def get_collecteur_badges(collecteur_id: int, db: Session = Depends(get_db)):
    """Gamification: badges obtenus ou en cours"""
    _ensure_collecteur(db, collecteur_id)
    badges = (
        db.query(BadgeCollecteur)
        .filter(BadgeCollecteur.collecteur_id == collecteur_id)
        .order_by(BadgeCollecteur.created_at.desc())
        .all()
    )

    if not badges:
        badges = [
            BadgeItem(
                code="starter",
                label="Première collecte",
                description="A réalisé sa première collecte",
                statut="locked",
                date_obtention=None,
            )
        ]
        return BadgesResponse(badges=badges)

    return BadgesResponse(
        badges=[
            BadgeItem(
                code=badge.code,
                label=badge.label,
                description=badge.description,
                statut=badge.statut.value if hasattr(badge.statut, "value") else badge.statut,
                date_obtention=badge.date_obtention,
            )
            for badge in badges
        ]
    )


@router.post(
    "/{collecteur_id}/performances/feedback",
    status_code=201,
)
def post_collecteur_performance_feedback(
    collecteur_id: int,
    payload: FeedbackRequest,
    db: Session = Depends(get_db),
):
    """Permet d'accuser réception d'un badge ou d'un palier franchi"""
    _ensure_collecteur(db, collecteur_id)
    if not payload.badge_code:
        raise HTTPException(status_code=400, detail="badge_code requis")

    feedback = BadgeFeedback(
        collecteur_id=collecteur_id,
        badge_code=payload.badge_code,
        feedback=payload.feedback,
    )
    db.add(feedback)
    db.commit()
    return {"status": "ok"}


@router.patch("/{collecteur_id}/position", response_model=CollecteurResponse)
def update_collecteur_position(
    collecteur_id: int,
    latitude: float,
    longitude: float,
    db: Session = Depends(get_db)
):
    """Met à jour la position GPS d'un collecteur (pour suivi en temps réel)"""
    db_collecteur = db.query(Collecteur).filter(Collecteur.id == collecteur_id).first()
    if not db_collecteur:
        raise HTTPException(status_code=404, detail="Collecteur non trouvé")
    
    from decimal import Decimal
    db_collecteur.latitude = Decimal(str(latitude))
    db_collecteur.longitude = Decimal(str(longitude))
    db_collecteur.geom = make_point(float(db_collecteur.longitude), float(db_collecteur.latitude))
    db_collecteur.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_collecteur)
    return db_collecteur


@router.patch("/{collecteur_id}/connexion", response_model=CollecteurResponse)
def connexion_collecteur(collecteur_id: int, db: Session = Depends(get_db)):
    """Connecte un collecteur"""
    db_collecteur = db.query(Collecteur).filter(Collecteur.id == collecteur_id).first()
    if not db_collecteur:
        raise HTTPException(status_code=404, detail="Collecteur non trouvé")
    
    if db_collecteur.statut != StatutCollecteurEnum.ACTIVE:
        raise HTTPException(status_code=400, detail="Le collecteur n'est pas actif")
    
    db_collecteur.etat = EtatCollecteurEnum.CONNECTE
    db_collecteur.date_derniere_connexion = datetime.utcnow()
    db_collecteur.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_collecteur)
    return db_collecteur


@router.patch("/{collecteur_id}/deconnexion", response_model=CollecteurResponse)
def deconnexion_collecteur(collecteur_id: int, db: Session = Depends(get_db)):
    """Déconnecte un collecteur"""
    db_collecteur = db.query(Collecteur).filter(Collecteur.id == collecteur_id).first()
    if not db_collecteur:
        raise HTTPException(status_code=404, detail="Collecteur non trouvé")
    
    db_collecteur.etat = EtatCollecteurEnum.DECONNECTE
    db_collecteur.date_derniere_deconnexion = datetime.utcnow()
    db_collecteur.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_collecteur)
    return db_collecteur


@router.delete("/{collecteur_id}", status_code=204)
def delete_collecteur(collecteur_id: int, db: Session = Depends(get_db)):
    """Supprime un collecteur (soft delete)"""
    db_collecteur = db.query(Collecteur).filter(Collecteur.id == collecteur_id).first()
    if not db_collecteur:
        raise HTTPException(status_code=404, detail="Collecteur non trouvé")
    
    db_collecteur.actif = False
    db_collecteur.statut = StatutCollecteurEnum.DESACTIVE
    db_collecteur.updated_at = datetime.utcnow()
    db.commit()
    return None


@router.get("/{collecteur_id}/activites", response_model=ActiviteCollecteurResponse)
def get_activites_collecteur(
    collecteur_id: int,
    date_debut: Optional[str] = Query(None, description="Date de début (YYYY-MM-DD). Par défaut: 30 derniers jours"),
    date_fin: Optional[str] = Query(None, description="Date de fin (YYYY-MM-DD). Par défaut: aujourd'hui"),
    db: Session = Depends(get_db)
):
    """
    Récupère les activités d'un collecteur (collectes par jour, heures de travail, etc.)
    """
    # Vérifier que le collecteur existe
    collecteur = db.query(Collecteur).filter(Collecteur.id == collecteur_id).first()
    if not collecteur:
        raise HTTPException(status_code=404, detail="Collecteur non trouvé")
    
    # Définir les dates par défaut (30 derniers jours)
    if not date_fin:
        date_fin = datetime.utcnow().date()
    else:
        try:
            date_fin = datetime.strptime(date_fin, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Format de date_fin invalide. Utilisez YYYY-MM-DD")
    
    if not date_debut:
        date_debut = date_fin - timedelta(days=30)
    else:
        try:
            date_debut = datetime.strptime(date_debut, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Format de date_debut invalide. Utilisez YYYY-MM-DD")
    
    # Récupérer les collectes du collecteur dans la période
    collectes = db.query(InfoCollecte).filter(
        InfoCollecte.collecteur_id == collecteur_id,
        InfoCollecte.annule == False,
        func.date(InfoCollecte.date_collecte) >= date_debut,
        func.date(InfoCollecte.date_collecte) <= date_fin
    ).order_by(InfoCollecte.date_collecte).all()
    
    # Grouper par jour
    activites_par_jour = {}
    for collecte in collectes:
        date_collecte = collecte.date_collecte.date()
        date_str = date_collecte.strftime("%Y-%m-%d")
        
        if date_str not in activites_par_jour:
            activites_par_jour[date_str] = {
                "date": date_str,
                "collectes": [],
                "montant_total": Decimal("0.00")
            }
        
        activites_par_jour[date_str]["collectes"].append(collecte)
        activites_par_jour[date_str]["montant_total"] += collecte.montant
    
    # Construire la liste des activités
    activites = []
    total_collectes = 0
    total_montant = Decimal("0.00")
    
    for date_str in sorted(activites_par_jour.keys()):
        jour_data = activites_par_jour[date_str]
        collectes_du_jour = jour_data["collectes"]
        
        # Trouver la première et dernière collecte du jour
        premiere_collecte = min(collectes_du_jour, key=lambda c: c.date_collecte).date_collecte
        derniere_collecte = max(collectes_du_jour, key=lambda c: c.date_collecte).date_collecte
        
        # Calculer la durée de travail en minutes
        duree_minutes = None
        if premiere_collecte and derniere_collecte:
            delta = derniere_collecte - premiere_collecte
            duree_minutes = int(delta.total_seconds() / 60)
        
        activite = ActiviteJour(
            date=date_str,
            nombre_collectes=len(collectes_du_jour),
            montant_total=jour_data["montant_total"],
            premiere_collecte=premiere_collecte,
            derniere_collecte=derniere_collecte,
            duree_travail_minutes=duree_minutes
        )
        activites.append(activite)
        
        total_collectes += len(collectes_du_jour)
        total_montant += jour_data["montant_total"]
    
    # Calculer les moyennes
    nombre_jours_actifs = len(activites)
    moyenne_collectes = total_collectes / nombre_jours_actifs if nombre_jours_actifs > 0 else None
    moyenne_montant = total_montant / nombre_jours_actifs if nombre_jours_actifs > 0 else None
    
    return ActiviteCollecteurResponse(
        collecteur_id=collecteur.id,
        collecteur_nom=collecteur.nom,
        collecteur_prenom=collecteur.prenom,
        collecteur_matricule=collecteur.matricule,
        periode_debut=date_debut.strftime("%Y-%m-%d"),
        periode_fin=date_fin.strftime("%Y-%m-%d"),
        activites=activites,
        total_collectes=total_collectes,
        total_montant=total_montant,
        nombre_jours_actifs=nombre_jours_actifs,
        moyenne_collectes_par_jour=moyenne_collectes,
        moyenne_montant_par_jour=moyenne_montant
    )


