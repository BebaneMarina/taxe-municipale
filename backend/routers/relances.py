"""
Routes pour la gestion des relances
"""

import os
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, or_
from typing import List, Optional
from database.database import get_db
from database.models import Relance, Contribuable, AffectationTaxe, InfoCollecte, StatutCollecteEnum, TypeRelanceEnum, StatutRelanceEnum
from schemas.relance import (
    RelanceCreate,
    RelanceUpdate,
    RelanceResponse,
    RelanceListResponse,
    RelanceManuelleRequest,
)
from datetime import datetime, date, timedelta
from decimal import Decimal
from services.ventis_messaging import ventis_messaging_service

router = APIRouter(prefix="/api/relances", tags=["relances"])
VENTIS_DEFAULT_SENDER = os.getenv("VENTIS_MESSAGING_SENDER", "VENTIS")


@router.get("/", response_model=RelanceListResponse)
def get_relances(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    contribuable_id: Optional[int] = None,
    affectation_taxe_id: Optional[int] = None,
    type_relance: Optional[str] = None,
    statut: Optional[str] = None,
    date_debut: Optional[date] = None,
    date_fin: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Récupère la liste des relances avec filtres"""
    query = db.query(Relance).options(
        joinedload(Relance.contribuable),
        joinedload(Relance.affectation_taxe)
    )
    
    if contribuable_id:
        query = query.filter(Relance.contribuable_id == contribuable_id)
    if affectation_taxe_id:
        query = query.filter(Relance.affectation_taxe_id == affectation_taxe_id)
    if type_relance:
        try:
            type_enum = TypeRelanceEnum(type_relance)
            query = query.filter(Relance.type_relance == type_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail="Type de relance invalide")
    if statut:
        try:
            statut_enum = StatutRelanceEnum(statut)
            query = query.filter(Relance.statut == statut_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail="Statut invalide")
    if date_debut:
        query = query.filter(Relance.date_planifiee >= datetime.combine(date_debut, datetime.min.time()))
    if date_fin:
        query = query.filter(Relance.date_planifiee <= datetime.combine(date_fin, datetime.max.time()))
    
    total = query.count()
    relances = query.order_by(Relance.date_planifiee.desc()).offset(skip).limit(limit).all()
    
    # Convertir les objets SQLAlchemy en schémas Pydantic avec from_attributes
    from schemas.relance import RelanceResponse
    relances_data = [RelanceResponse.model_validate(relance, from_attributes=True) for relance in relances]
    
    return RelanceListResponse(
        items=relances_data,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{relance_id}", response_model=RelanceResponse)
def get_relance(relance_id: int, db: Session = Depends(get_db)):
    """Récupère une relance par son ID"""
    relance = db.query(Relance).options(
        joinedload(Relance.contribuable),
        joinedload(Relance.affectation_taxe)
    ).filter(Relance.id == relance_id).first()
    
    if not relance:
        raise HTTPException(status_code=404, detail="Relance non trouvée")
    return RelanceResponse.model_validate(relance, from_attributes=True)


@router.post("/", response_model=RelanceResponse, status_code=201)
def create_relance(relance: RelanceCreate, db: Session = Depends(get_db)):
    """Crée une nouvelle relance"""
    # Vérifier que le contribuable existe
    contribuable = db.query(Contribuable).filter(Contribuable.id == relance.contribuable_id).first()
    if not contribuable:
        raise HTTPException(status_code=404, detail="Contribuable non trouvé")
    
    # Vérifier l'affectation si fournie
    if relance.affectation_taxe_id:
        affectation = db.query(AffectationTaxe).filter(AffectationTaxe.id == relance.affectation_taxe_id).first()
        if not affectation:
            raise HTTPException(status_code=404, detail="Affectation de taxe non trouvée")
    
    db_relance = Relance(**relance.dict())
    db.add(db_relance)
    db.commit()
    db.refresh(db_relance)
    # Recharger avec les relations
    db_relance = db.query(Relance).options(
        joinedload(Relance.contribuable),
        joinedload(Relance.affectation_taxe)
    ).filter(Relance.id == db_relance.id).first()
    return RelanceResponse.model_validate(db_relance, from_attributes=True)


@router.put("/{relance_id}", response_model=RelanceResponse)
def update_relance(relance_id: int, relance_update: RelanceUpdate, db: Session = Depends(get_db)):
    """Met à jour une relance"""
    db_relance = db.query(Relance).filter(Relance.id == relance_id).first()
    if not db_relance:
        raise HTTPException(status_code=404, detail="Relance non trouvée")
    
    update_data = relance_update.dict(exclude_unset=True)
    
    # Gérer les enums
    if "statut" in update_data:
        try:
            update_data["statut"] = StatutRelanceEnum(update_data["statut"])
        except ValueError:
            raise HTTPException(status_code=400, detail="Statut invalide")
    
    for field, value in update_data.items():
        setattr(db_relance, field, value)
    
    db_relance.updated_at = datetime.utcnow()
    db.commit()
    # Recharger avec les relations
    db_relance = db.query(Relance).options(
        joinedload(Relance.contribuable),
        joinedload(Relance.affectation_taxe)
    ).filter(Relance.id == relance_id).first()
    return RelanceResponse.model_validate(db_relance, from_attributes=True)


@router.patch("/{relance_id}/envoyer", response_model=RelanceResponse)
async def envoyer_relance(relance_id: int, db: Session = Depends(get_db)):
    """Envoie une relance via l'API Ventis et met à jour le statut"""
    db_relance = db.query(Relance).options(
        joinedload(Relance.contribuable),
        joinedload(Relance.affectation_taxe)
    ).filter(Relance.id == relance_id).first()
    
    if not db_relance:
        raise HTTPException(status_code=404, detail="Relance non trouvée")
    
    if db_relance.statut == StatutRelanceEnum.ENVOYEE:
        raise HTTPException(status_code=400, detail="Cette relance a déjà été envoyée")
    
    # Envoyer le SMS si c'est une relance SMS et que le contribuable a un téléphone
    if db_relance.type_relance == TypeRelanceEnum.SMS and db_relance.contribuable and db_relance.contribuable.telephone:
        try:
            # Formater le numéro de téléphone
            phone = ventis_messaging_service.format_phone_number(db_relance.contribuable.telephone)
            
            # Construire le message
            message = db_relance.message or f"Rappel: Vous avez une taxe de {db_relance.montant_due} FCFA à payer."
            if db_relance.date_echeance:
                message += f" Échéance: {db_relance.date_echeance.strftime('%d/%m/%Y')}"
            
            # Envoyer le SMS
            result = await ventis_messaging_service.send_message(
                to=phone,
                message=message,
                sender=VENTIS_DEFAULT_SENDER,
                is_otp=False
            )
            
            if result.get('success'):
                # SMS envoyé avec succès
                db_relance.statut = StatutRelanceEnum.ENVOYEE
                db_relance.date_envoi = datetime.utcnow()
                db_relance.canal_envoi = phone
                db_relance.notes = f"SMS envoyé via Ventis. UUID: {result.get('data', {}).get('uuid', 'N/A')}"
            else:
                # Erreur lors de l'envoi - marquer comme échec
                db_relance.statut = StatutRelanceEnum.ECHEC
                error_detail = result.get('detail', 'Erreur inconnue')
                db_relance.notes = f"Erreur envoi SMS: {error_detail}"
                # Logger l'erreur
                import logging
                logging.error(f"Erreur envoi SMS pour relance {relance_id}: {error_detail}")
                # Ne pas lever d'exception - continuer pour sauvegarder le statut
        except Exception as e:
            # En cas d'exception, marquer comme échec
            db_relance.statut = StatutRelanceEnum.ECHEC
            db_relance.notes = f"Exception lors de l'envoi SMS: {str(e)}"
            # Logger l'erreur avec la stack trace
            import logging
            logging.error(f"Exception lors de l'envoi SMS pour relance {relance_id}: {str(e)}", exc_info=True)
            # Ne pas lever d'exception - continuer pour sauvegarder le statut
    else:
        # Pour les autres types de relances (email, appel, etc.), on marque juste comme envoyée
        db_relance.statut = StatutRelanceEnum.ENVOYEE
        db_relance.date_envoi = datetime.utcnow()
    
    db_relance.updated_at = datetime.utcnow()
    
    # Mettre à jour le nombre de relances dans le dossier d'impayé si existe
    if db_relance.affectation_taxe_id:
        from database.models import DossierImpaye
        dossier = db.query(DossierImpaye).filter(
            DossierImpaye.affectation_taxe_id == db_relance.affectation_taxe_id,
            DossierImpaye.statut == "en_cours"
        ).first()
        if dossier:
            dossier.nombre_relances += 1
            dossier.dernier_contact = datetime.utcnow()
    
    db.commit()
    # Recharger avec les relations
    db_relance = db.query(Relance).options(
        joinedload(Relance.contribuable),
        joinedload(Relance.affectation_taxe)
    ).filter(Relance.id == relance_id).first()
    return RelanceResponse.model_validate(db_relance, from_attributes=True)


@router.post("/generer-automatique", response_model=List[RelanceResponse])
async def generer_relances_automatiques(
    jours_retard_min: int = Query(7, ge=0, description="Nombre minimum de jours de retard"),
    type_relance: str = Query("sms", description="Type de relance à générer"),
    limite: int = Query(50, ge=1, le=500, description="Nombre maximum de relances à générer"),
    envoyer_automatiquement: bool = Query(False, description="Envoyer automatiquement les SMS après génération"),
    db: Session = Depends(get_db)
):
    """Génère automatiquement des relances pour les contribuables en retard"""
    try:
        type_enum = TypeRelanceEnum(type_relance)
    except ValueError:
        raise HTTPException(status_code=400, detail="Type de relance invalide")
    
    # Date limite : aujourd'hui - jours_retard_min
    date_limite = datetime.utcnow() - timedelta(days=jours_retard_min)
    
    # Trouver les affectations de taxes avec échéance dépassée et pas encore payées
    affectations_en_retard = db.query(AffectationTaxe).filter(
        AffectationTaxe.actif == True,
        AffectationTaxe.date_debut <= date_limite,
        or_(
            AffectationTaxe.date_fin.is_(None),
            AffectationTaxe.date_fin >= date_limite
        )
    ).limit(limite).all()
    
    relances_creees = []
    
    for affectation in affectations_en_retard:
        # Vérifier si une collecte complète existe pour cette affectation
        collecte_complete = db.query(InfoCollecte).filter(
            InfoCollecte.contribuable_id == affectation.contribuable_id,
            InfoCollecte.taxe_id == affectation.taxe_id,
            InfoCollecte.statut == StatutCollecteEnum.COMPLETED,
            InfoCollecte.annule == False,
            InfoCollecte.date_collecte >= affectation.date_debut
        ).first()
        
        # Si pas de collecte complète, créer une relance
        if not collecte_complete:
            # Vérifier si une relance récente existe déjà (moins de 7 jours)
            relance_recente = db.query(Relance).filter(
                Relance.affectation_taxe_id == affectation.id,
                Relance.date_planifiee >= datetime.utcnow() - timedelta(days=7)
            ).first()
            
            if not relance_recente:
                # Calculer le montant dû
                montant_due = affectation.montant_custom if affectation.montant_custom else affectation.taxe.montant
                
                # Calculer la date d'échéance (date_debut + période selon périodicité)
                date_echeance = affectation.date_debut
                if affectation.taxe.periodicite == "mensuelle":
                    date_echeance = affectation.date_debut + timedelta(days=30)
                elif affectation.taxe.periodicite == "hebdomadaire":
                    date_echeance = affectation.date_debut + timedelta(days=7)
                elif affectation.taxe.periodicite == "trimestrielle":
                    date_echeance = affectation.date_debut + timedelta(days=90)
                
                # Créer la relance
                nouvelle_relance = Relance(
                    contribuable_id=affectation.contribuable_id,
                    affectation_taxe_id=affectation.id,
                    type_relance=type_enum,
                    montant_due=montant_due,
                    date_echeance=date_echeance,
                    date_planifiee=datetime.utcnow(),
                    message=f"Rappel : Vous avez une taxe de {montant_due} FCFA à payer. Échéance : {date_echeance.strftime('%d/%m/%Y')}",
                    canal_envoi=affectation.contribuable.telephone if type_enum == TypeRelanceEnum.SMS else affectation.contribuable.email
                )
                db.add(nouvelle_relance)
                relances_creees.append(nouvelle_relance)
    
    db.commit()
    
    # Recharger avec les relations
    relances_ids = [r.id for r in relances_creees]
    relances_chargees = db.query(Relance).options(
        joinedload(Relance.contribuable),
        joinedload(Relance.affectation_taxe)
    ).filter(Relance.id.in_(relances_ids)).all()
    
    # Si envoyer_automatiquement est True, envoyer les SMS
    if envoyer_automatiquement and type_enum == TypeRelanceEnum.SMS:
        for relance in relances_chargees:
            if relance.contribuable and relance.contribuable.telephone:
                try:
                    # Formater le numéro de téléphone
                    phone = ventis_messaging_service.format_phone_number(relance.contribuable.telephone)
                    
                    # Construire le message
                    message = relance.message or f"Rappel: Vous avez une taxe de {relance.montant_due} FCFA à payer."
                    if relance.date_echeance:
                        message += f" Échéance: {relance.date_echeance.strftime('%d/%m/%Y')}"
                    
                    # Envoyer le SMS
                    result = await ventis_messaging_service.send_message(
                        to=phone,
                        message=message,
                        sender=VENTIS_DEFAULT_SENDER,
                        is_otp=False
                    )
                    
                    if result.get('success'):
                        # Mettre à jour le statut de la relance
                        relance.statut = StatutRelanceEnum.ENVOYEE
                        relance.date_envoi = datetime.utcnow()
                        relance.canal_envoi = phone
                        relance.notes = f"SMS envoyé via Ventis. UUID: {result.get('data', {}).get('uuid', 'N/A')}"
                    else:
                        # Erreur lors de l'envoi
                        relance.statut = StatutRelanceEnum.ECHEC
                        relance.notes = f"Erreur envoi SMS: {result.get('detail', 'Erreur inconnue')}"
                    
                    relance.updated_at = datetime.utcnow()
                    
                    # Mettre à jour le nombre de relances dans le dossier d'impayé si existe
                    if relance.affectation_taxe_id:
                        from database.models import DossierImpaye
                        dossier = db.query(DossierImpaye).filter(
                            DossierImpaye.affectation_taxe_id == relance.affectation_taxe_id,
                            DossierImpaye.statut == "en_cours"
                        ).first()
                        if dossier:
                            dossier.nombre_relances += 1
                            dossier.dernier_contact = datetime.utcnow()
                    
                except Exception as e:
                    # En cas d'erreur, marquer comme échec
                    relance.statut = StatutRelanceEnum.ECHEC
                    relance.notes = f"Exception lors de l'envoi: {str(e)}"
                    relance.updated_at = datetime.utcnow()
        
        db.commit()
        # Recharger les relances après mise à jour
        relances_chargees = db.query(Relance).options(
            joinedload(Relance.contribuable),
            joinedload(Relance.affectation_taxe)
        ).filter(Relance.id.in_(relances_ids)).all()
    
    return [RelanceResponse.model_validate(relance, from_attributes=True) for relance in relances_chargees]


@router.get("/contribuable/{contribuable_id}/historique", response_model=List[RelanceResponse])
def get_historique_relances_contribuable(
    contribuable_id: int,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Récupère l'historique des relances pour un contribuable"""
    relances = db.query(Relance).options(
        joinedload(Relance.contribuable),
        joinedload(Relance.affectation_taxe)
    ).filter(
        Relance.contribuable_id == contribuable_id
    ).order_by(Relance.date_planifiee.desc()).limit(limit).all()
    
    return [RelanceResponse.model_validate(relance, from_attributes=True) for relance in relances]


@router.get("/statistiques", response_model=dict)
def get_statistiques_relances(
    date_debut: Optional[str] = Query(None, description="Date de début pour les statistiques (format: YYYY-MM-DD)"),
    date_fin: Optional[str] = Query(None, description="Date de fin pour les statistiques (format: YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """Récupère les statistiques sur les relances"""
    query = db.query(Relance)
    
    # Convertir les chaînes en dates si fournies
    date_debut_obj = None
    date_fin_obj = None
    
    if date_debut and date_debut.strip():
        try:
            date_debut_obj = datetime.strptime(date_debut.strip(), "%Y-%m-%d").date()
            query = query.filter(Relance.date_planifiee >= datetime.combine(date_debut_obj, datetime.min.time()))
        except ValueError:
            raise HTTPException(status_code=400, detail="Format de date_debut invalide. Utilisez YYYY-MM-DD")
    
    if date_fin and date_fin.strip():
        try:
            date_fin_obj = datetime.strptime(date_fin.strip(), "%Y-%m-%d").date()
            query = query.filter(Relance.date_planifiee <= datetime.combine(date_fin_obj, datetime.max.time()))
        except ValueError:
            raise HTTPException(status_code=400, detail="Format de date_fin invalide. Utilisez YYYY-MM-DD")
    
    total_relances = query.count()
    relances_envoyees = query.filter(Relance.statut == StatutRelanceEnum.ENVOYEE).count()
    relances_en_attente = query.filter(Relance.statut == StatutRelanceEnum.EN_ATTENTE).count()
    relances_avec_reponse = query.filter(Relance.reponse_recue == True).count()
    
    # Par type
    par_type = {}
    for type_rel in TypeRelanceEnum:
        count = query.filter(Relance.type_relance == type_rel).count()
        par_type[type_rel.value] = count
    
    return {
        "total_relances": total_relances,
        "relances_envoyees": relances_envoyees,
        "relances_en_attente": relances_en_attente,
        "relances_avec_reponse": relances_avec_reponse,
        "taux_reponse": (relances_avec_reponse / total_relances * 100) if total_relances > 0 else 0,
        "par_type": par_type
    }


@router.post("/manuelles", response_model=List[RelanceResponse], status_code=201)
def creer_relances_manuelles(
    payload: RelanceManuelleRequest,
    db: Session = Depends(get_db),
):
    """Crée plusieurs relances manuelles en sélectionnant n'importe quels contribuables."""
    try:
        type_enum = TypeRelanceEnum(payload.type_relance)
    except ValueError:
        raise HTTPException(status_code=400, detail="Type de relance invalide")

    if not payload.contribuables:
        raise HTTPException(status_code=400, detail="Merci de sélectionner au moins un contribuable")

    date_planifiee = payload.date_planifiee or datetime.utcnow()
    created_ids: List[int] = []

    for item in payload.contribuables:
        contribuable = (
            db.query(Contribuable)
            .filter(Contribuable.id == item.contribuable_id)
            .first()
        )
        if not contribuable:
            raise HTTPException(
                status_code=404,
                detail=f"Contribuable {item.contribuable_id} introuvable",
            )

        montant = item.montant_due or payload.montant_due
        if montant is None:
            raise HTTPException(
                status_code=400,
                detail="Merci d'indiquer un montant dû (global ou par contribuable)",
            )

        message = item.message or payload.message
        if not message:
            message = f"Rappel : vous avez une somme de {montant} FCFA à payer."

        relance = Relance(
            contribuable_id=item.contribuable_id,
            type_relance=type_enum,
            montant_due=montant,
            date_echeance=item.date_echeance or payload.date_echeance,
            date_planifiee=date_planifiee,
            message=message,
            utilisateur_id=payload.utilisateur_id,
            canal_envoi=item.telephone_override or contribuable.telephone,
            notes=item.notes or payload.notes,
        )
        db.add(relance)
        db.flush()
        created_ids.append(relance.id)

    db.commit()

    relances = (
        db.query(Relance)
        .options(
            joinedload(Relance.contribuable),
            joinedload(Relance.affectation_taxe),
        )
        .filter(Relance.id.in_(created_ids))
        .all()
    )
    return [
        RelanceResponse.model_validate(relance, from_attributes=True)
        for relance in relances
    ]

