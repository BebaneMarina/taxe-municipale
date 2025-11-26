"""
Routes pour la gestion des caisses des collecteurs
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from database.database import get_db
from database.models import (
    Caisse,
    OperationCaisse,
    Collecteur,
    TypeCaisseEnum,
    EtatCaisseEnum,
    TypeOperationCaisseEnum,
    CoupureCaisse,
    TypeCoupureEnum,
)
from schemas.caisse import (
    CaisseCreate, CaisseUpdate, CaisseResponse,
    OperationCaisseCreate, OperationCaisseResponse,
    EtatCaisseResponse, CaissesListResponse
)
from schemas.coupure import (
    CoupureCreate,
    CoupureUpdate,
    CoupureResponse,
    CoupuresListResponse,
)
from auth.security import get_current_active_user

router = APIRouter(
    prefix="/api/caisses",
    tags=["caisses"],
    dependencies=[Depends(get_current_active_user)],
)


@router.get("/", response_model=CaissesListResponse)
def get_caisses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    collecteur_id: Optional[int] = None,
    type_caisse: Optional[str] = None,
    etat: Optional[str] = None,
    actif: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Récupère la liste des caisses avec filtres"""
    from sqlalchemy.orm import joinedload
    
    query = db.query(Caisse).options(joinedload(Caisse.collecteur))
    
    if collecteur_id:
        query = query.filter(Caisse.collecteur_id == collecteur_id)
    if type_caisse:
        query = query.filter(Caisse.type_caisse == type_caisse)
    if etat:
        query = query.filter(Caisse.etat == etat)
    if actif is not None:
        query = query.filter(Caisse.actif == actif)
    
    total = query.count()
    caisses = query.order_by(desc(Caisse.created_at)).offset(skip).limit(limit).all()
    
    return CaissesListResponse(
        items=caisses,
        total=total,
        skip=skip,
        limit=limit
    )


def _validate_coupure_type(type_coupure: str):
    allowed = [e.value for e in TypeCoupureEnum]
    if type_coupure not in allowed:
        raise HTTPException(status_code=400, detail=f"Type de coupure invalide. Valeurs acceptées: {allowed}")


def _get_coupure_or_404(coupure_id: int, db: Session) -> CoupureCaisse:
    coupure = db.query(CoupureCaisse).filter(CoupureCaisse.id == coupure_id).first()
    if not coupure:
        raise HTTPException(status_code=404, detail="Coupure non trouvée")
    return coupure


@router.get("/coupures", response_model=CoupuresListResponse)
def list_coupures(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    actif: Optional[bool] = None,
    type_coupure: Optional[str] = None,
    devise: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Liste les coupures paramétrées"""
    query = db.query(CoupureCaisse)

    if actif is not None:
        query = query.filter(CoupureCaisse.actif == actif)

    if type_coupure:
        _validate_coupure_type(type_coupure)
        query = query.filter(CoupureCaisse.type_coupure == type_coupure)

    if devise:
        query = query.filter(func.upper(CoupureCaisse.devise) == devise.upper())

    total = query.count()
    items = (
        query.order_by(CoupureCaisse.ordre_affichage.asc(), CoupureCaisse.valeur.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return CoupuresListResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/coupures/{coupure_id}", response_model=CoupureResponse)
def get_coupure(coupure_id: int, db: Session = Depends(get_db)):
    """Récupère une coupure par ID"""
    coupure = _get_coupure_or_404(coupure_id, db)
    return coupure


@router.post("/coupures", response_model=CoupureResponse, status_code=201)
def create_coupure(coupure: CoupureCreate, db: Session = Depends(get_db)):
    """Crée une nouvelle coupure"""
    _validate_coupure_type(coupure.type_coupure)
    devise = coupure.devise.upper()

    existing = (
        db.query(CoupureCaisse)
        .filter(
            CoupureCaisse.valeur == coupure.valeur,
            func.upper(CoupureCaisse.devise) == devise,
            CoupureCaisse.type_coupure == coupure.type_coupure,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Cette coupure existe déjà")

    if coupure.ordre_affichage is None:
        max_order = db.query(func.coalesce(func.max(CoupureCaisse.ordre_affichage), -1)).scalar() or -1
        ordre_affichage = max_order + 1
    else:
        ordre_affichage = coupure.ordre_affichage

    db_coupure = CoupureCaisse(
        valeur=coupure.valeur,
        devise=devise,
        type_coupure=coupure.type_coupure,
        description=coupure.description,
        ordre_affichage=ordre_affichage,
        actif=coupure.actif,
    )

    db.add(db_coupure)
    db.commit()
    db.refresh(db_coupure)
    return db_coupure


@router.put("/coupures/{coupure_id}", response_model=CoupureResponse)
def update_coupure(coupure_id: int, coupure_update: CoupureUpdate, db: Session = Depends(get_db)):
    """Met à jour une coupure"""
    coupure = _get_coupure_or_404(coupure_id, db)

    update_data = coupure_update.dict(exclude_unset=True)

    if "type_coupure" in update_data and update_data["type_coupure"]:
        _validate_coupure_type(update_data["type_coupure"])

    if "devise" in update_data and update_data["devise"]:
        update_data["devise"] = update_data["devise"].upper()

    for field, value in update_data.items():
        setattr(coupure, field, value)

    # Vérifier l'unicité après mise à jour
    duplicate = (
        db.query(CoupureCaisse)
        .filter(
            CoupureCaisse.id != coupure.id,
            CoupureCaisse.valeur == coupure.valeur,
            func.upper(CoupureCaisse.devise) == coupure.devise.upper(),
            CoupureCaisse.type_coupure == coupure.type_coupure,
        )
        .first()
    )
    if duplicate:
        raise HTTPException(status_code=400, detail="Une coupure avec ces paramètres existe déjà")

    coupure.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(coupure)
    return coupure


@router.patch("/coupures/{coupure_id}/toggle", response_model=CoupureResponse)
def toggle_coupure_activation(coupure_id: int, db: Session = Depends(get_db)):
    """Active/Désactive une coupure"""
    coupure = _get_coupure_or_404(coupure_id, db)
    coupure.actif = not coupure.actif
    coupure.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(coupure)
    return coupure


@router.delete("/coupures/{coupure_id}", status_code=204)
def delete_coupure(coupure_id: int, db: Session = Depends(get_db)):
    """Supprime une coupure"""
    coupure = _get_coupure_or_404(coupure_id, db)
    db.delete(coupure)
    db.commit()
    return None


@router.get("/{caisse_id}", response_model=CaisseResponse)
def get_caisse(caisse_id: int, db: Session = Depends(get_db)):
    """Récupère une caisse par son ID"""
    from sqlalchemy.orm import joinedload
    
    caisse = db.query(Caisse).options(joinedload(Caisse.collecteur)).filter(Caisse.id == caisse_id).first()
    if not caisse:
        raise HTTPException(status_code=404, detail="Caisse non trouvée")
    return caisse


@router.get("/{caisse_id}/etat", response_model=EtatCaisseResponse)
def get_etat_caisse(caisse_id: int, db: Session = Depends(get_db)):
    """Récupère l'état détaillé d'une caisse avec statistiques"""
    from sqlalchemy.orm import joinedload
    
    caisse = db.query(Caisse).options(joinedload(Caisse.collecteur)).filter(Caisse.id == caisse_id).first()
    if not caisse:
        raise HTTPException(status_code=404, detail="Caisse non trouvée")
    
    # Calculer les statistiques
    operations = db.query(OperationCaisse).filter(OperationCaisse.caisse_id == caisse_id).all()
    
    total_entrees = sum(
        op.montant for op in operations 
        if op.type_operation in [TypeOperationCaisseEnum.ENTREE.value, TypeOperationCaisseEnum.OUVERTURE.value]
    ) or Decimal('0')
    
    total_sorties = sum(
        op.montant for op in operations 
        if op.type_operation in [TypeOperationCaisseEnum.SORTIE.value, TypeOperationCaisseEnum.FERMETURE.value]
    ) or Decimal('0')
    
    solde_theorique = caisse.solde_initial + total_entrees - total_sorties
    
    # Opérations récentes (10 dernières)
    operations_recentes = (
        db.query(OperationCaisse)
        .filter(OperationCaisse.caisse_id == caisse_id)
        .order_by(desc(OperationCaisse.date_operation))
        .limit(10)
        .all()
    )
    
    return EtatCaisseResponse(
        caisse=caisse,
        nombre_operations=len(operations),
        total_entrees=total_entrees,
        total_sorties=total_sorties,
        solde_theorique=solde_theorique,
        operations_recentes=operations_recentes
    )


@router.post("/", response_model=CaisseResponse, status_code=201)
def create_caisse(caisse: CaisseCreate, db: Session = Depends(get_db)):
    """Crée une nouvelle caisse"""
    from sqlalchemy.orm import joinedload
    
    # Vérifier que le collecteur existe
    collecteur = db.query(Collecteur).filter(Collecteur.id == caisse.collecteur_id).first()
    if not collecteur:
        raise HTTPException(status_code=404, detail="Collecteur non trouvé")
    
    # Vérifier que le code est unique
    existing = db.query(Caisse).filter(Caisse.code == caisse.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Une caisse avec ce code existe déjà")
    
    # Vérifier le type de caisse
    if caisse.type_caisse not in [e.value for e in TypeCaisseEnum]:
        raise HTTPException(status_code=400, detail=f"Type de caisse invalide. Valeurs acceptées: {[e.value for e in TypeCaisseEnum]}")
    
    db_caisse = Caisse(**caisse.dict())
    db.add(db_caisse)
    db.commit()
    db.refresh(db_caisse)
    
    # Recharger avec les relations
    db_caisse = db.query(Caisse).options(joinedload(Caisse.collecteur)).filter(Caisse.id == db_caisse.id).first()
    return db_caisse


@router.put("/{caisse_id}", response_model=CaisseResponse)
def update_caisse(caisse_id: int, caisse_update: CaisseUpdate, db: Session = Depends(get_db)):
    """Met à jour une caisse"""
    from sqlalchemy.orm import joinedload
    
    db_caisse = db.query(Caisse).filter(Caisse.id == caisse_id).first()
    if not db_caisse:
        raise HTTPException(status_code=404, detail="Caisse non trouvée")
    
    update_data = caisse_update.dict(exclude_unset=True)
    
    # Vérifier l'état si fourni
    if "etat" in update_data:
        if update_data["etat"] not in [e.value for e in EtatCaisseEnum]:
            raise HTTPException(status_code=400, detail=f"État invalide. Valeurs acceptées: {[e.value for e in EtatCaisseEnum]}")
    
    for field, value in update_data.items():
        setattr(db_caisse, field, value)
    
    db_caisse.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_caisse)
    
    # Recharger avec les relations
    db_caisse = db.query(Caisse).options(joinedload(Caisse.collecteur)).filter(Caisse.id == caisse_id).first()
    return db_caisse


@router.post("/{caisse_id}/ouvrir", response_model=OperationCaisseResponse)
def ouvrir_caisse(
    caisse_id: int,
    solde_initial: Decimal = Query(0.00, description="Solde initial à l'ouverture"),
    db: Session = Depends(get_db)
):
    """Ouvre une caisse"""
    caisse = db.query(Caisse).filter(Caisse.id == caisse_id).first()
    if not caisse:
        raise HTTPException(status_code=404, detail="Caisse non trouvée")
    
    if caisse.etat == EtatCaisseEnum.OUVERTE.value:
        raise HTTPException(status_code=400, detail="La caisse est déjà ouverte")
    
    # Créer l'opération d'ouverture
    operation = OperationCaisse(
        caisse_id=caisse_id,
        collecteur_id=caisse.collecteur_id,
        type_operation=TypeOperationCaisseEnum.OUVERTURE.value,
        montant=solde_initial,
        libelle=f"Ouverture de caisse - Solde initial: {solde_initial}",
        solde_avant=Decimal('0'),
        solde_apres=solde_initial
    )
    
    # Mettre à jour la caisse
    caisse.etat = EtatCaisseEnum.OUVERTE.value
    caisse.solde_initial = solde_initial
    caisse.solde_actuel = solde_initial
    caisse.date_ouverture = datetime.utcnow()
    
    db.add(operation)
    db.commit()
    db.refresh(operation)
    
    return operation


@router.post("/{caisse_id}/fermer", response_model=OperationCaisseResponse)
def fermer_caisse(
    caisse_id: int,
    notes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Ferme une caisse"""
    caisse = db.query(Caisse).filter(Caisse.id == caisse_id).first()
    if not caisse:
        raise HTTPException(status_code=404, detail="Caisse non trouvée")
    
    if caisse.etat != EtatCaisseEnum.OUVERTE.value:
        raise HTTPException(status_code=400, detail="La caisse n'est pas ouverte")
    
    # Calculer le solde actuel
    solde_actuel = caisse.solde_actuel
    
    # Créer l'opération de fermeture
    operation = OperationCaisse(
        caisse_id=caisse_id,
        collecteur_id=caisse.collecteur_id,
        type_operation=TypeOperationCaisseEnum.FERMETURE.value,
        montant=solde_actuel,
        libelle=f"Fermeture de caisse - Solde: {solde_actuel}",
        solde_avant=solde_actuel,
        solde_apres=Decimal('0'),
        notes=notes
    )
    
    # Mettre à jour la caisse
    caisse.etat = EtatCaisseEnum.FERMEE.value
    caisse.date_fermeture = datetime.utcnow()
    
    db.add(operation)
    db.commit()
    db.refresh(operation)
    
    return operation


@router.post("/{caisse_id}/cloturer", response_model=OperationCaisseResponse)
def cloturer_caisse(
    caisse_id: int,
    montant_cloture: Decimal = Query(..., description="Montant à la clôture"),
    notes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Clôture une caisse (fin de journée)"""
    caisse = db.query(Caisse).filter(Caisse.id == caisse_id).first()
    if not caisse:
        raise HTTPException(status_code=404, detail="Caisse non trouvée")
    
    if caisse.etat != EtatCaisseEnum.OUVERTE.value:
        raise HTTPException(status_code=400, detail="La caisse doit être ouverte pour être clôturée")
    
    solde_avant = caisse.solde_actuel
    
    # Créer l'opération de clôture
    operation = OperationCaisse(
        caisse_id=caisse_id,
        collecteur_id=caisse.collecteur_id,
        type_operation=TypeOperationCaisseEnum.CLOTURE.value,
        montant=montant_cloture,
        libelle=f"Clôture de caisse - Montant: {montant_cloture}",
        solde_avant=solde_avant,
        solde_apres=montant_cloture,
        notes=notes
    )
    
    # Mettre à jour la caisse
    caisse.etat = EtatCaisseEnum.CLOTUREE.value
    caisse.date_cloture = datetime.utcnow()
    caisse.montant_cloture = montant_cloture
    
    db.add(operation)
    db.commit()
    db.refresh(operation)
    
    return operation


@router.post("/{caisse_id}/operations", response_model=OperationCaisseResponse)
def create_operation_caisse(
    caisse_id: int,
    operation: OperationCaisseCreate,
    db: Session = Depends(get_db)
):
    """Crée une opération de caisse (entrée, sortie, ajustement)"""
    caisse = db.query(Caisse).filter(Caisse.id == caisse_id).first()
    if not caisse:
        raise HTTPException(status_code=404, detail="Caisse non trouvée")
    
    if caisse.etat != EtatCaisseEnum.OUVERTE.value:
        raise HTTPException(status_code=400, detail="La caisse doit être ouverte pour effectuer des opérations")
    
    # Vérifier le type d'opération
    if operation.type_operation not in [
        TypeOperationCaisseEnum.ENTREE.value,
        TypeOperationCaisseEnum.SORTIE.value,
        TypeOperationCaisseEnum.AJUSTEMENT.value
    ]:
        raise HTTPException(status_code=400, detail="Type d'opération invalide pour cette route. Utilisez /ouvrir, /fermer ou /cloturer")
    
    solde_avant = caisse.solde_actuel
    
    # Calculer le nouveau solde
    if operation.type_operation == TypeOperationCaisseEnum.ENTREE.value:
        solde_apres = solde_avant + operation.montant
    elif operation.type_operation == TypeOperationCaisseEnum.SORTIE.value:
        solde_apres = solde_avant - operation.montant
        if solde_apres < 0:
            raise HTTPException(status_code=400, detail="Solde insuffisant")
    else:  # AJUSTEMENT
        solde_apres = operation.montant
    
    # Créer l'opération
    db_operation = OperationCaisse(
        caisse_id=caisse_id,
        collecteur_id=caisse.collecteur_id,
        type_operation=operation.type_operation,
        montant=operation.montant,
        libelle=operation.libelle,
        collecte_id=operation.collecte_id,
        reference=operation.reference,
        notes=operation.notes,
        solde_avant=solde_avant,
        solde_apres=solde_apres
    )
    
    # Mettre à jour le solde de la caisse
    caisse.solde_actuel = solde_apres
    caisse.updated_at = datetime.utcnow()
    
    db.add(db_operation)
    db.commit()
    db.refresh(db_operation)
    
    return db_operation


@router.get("/{caisse_id}/operations", response_model=List[OperationCaisseResponse])
def get_operations_caisse(
    caisse_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    type_operation: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Récupère les opérations d'une caisse"""
    query = db.query(OperationCaisse).filter(OperationCaisse.caisse_id == caisse_id)
    
    if type_operation:
        query = query.filter(OperationCaisse.type_operation == type_operation)
    
    operations = query.order_by(desc(OperationCaisse.date_operation)).offset(skip).limit(limit).all()
    return operations


@router.delete("/{caisse_id}", status_code=204)
def delete_caisse(caisse_id: int, db: Session = Depends(get_db)):
    """Supprime une caisse (soft delete)"""
    caisse = db.query(Caisse).filter(Caisse.id == caisse_id).first()
    if not caisse:
        raise HTTPException(status_code=404, detail="Caisse non trouvée")
    
    if caisse.etat == EtatCaisseEnum.OUVERTE.value:
        raise HTTPException(status_code=400, detail="Impossible de supprimer une caisse ouverte")
    
    caisse.actif = False
    caisse.updated_at = datetime.utcnow()
    db.commit()
    return None

