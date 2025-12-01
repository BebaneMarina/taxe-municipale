"""
Routes pour la gestion des contribuables
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Tuple
from database.database import get_db
from database.models import Contribuable
from schemas.contribuable import ContribuableCreate, ContribuableUpdate, ContribuableResponse
from datetime import datetime
from auth.security import get_current_active_user
from services.qr_code_service import generate_qr_code_string, generate_qr_code_image, generate_qr_code_with_info

router = APIRouter(
    prefix="/api/contribuables",
    tags=["contribuables"],
    dependencies=[Depends(get_current_active_user)],
)


def make_point(longitude: Optional[float], latitude: Optional[float]):
    if longitude is None or latitude is None:
        return None
    return func.ST_SetSRID(func.ST_MakePoint(longitude, latitude), 4326)


def find_nearest_quartier(db: Session, geom_point) -> Tuple[Optional[int], Optional[float]]:
    """Retourne le quartier le plus proche et la distance en mètres."""
    if geom_point is None:
        return None, None
    from database.models import Quartier

    row = (
        db.query(
            Quartier.id,
            func.ST_DistanceSphere(Quartier.geom, geom_point).label("distance_m"),
        )
        .filter(Quartier.geom.isnot(None))
        .order_by(func.ST_DistanceSphere(Quartier.geom, geom_point))
        .limit(1)
        .first()
    )
    if not row or row.distance_m is None:
        return None, None
    return row.id, float(row.distance_m)


def distance_to_quartier(db: Session, quartier_id: Optional[int], geom_point) -> Optional[float]:
    if not quartier_id or geom_point is None:
        return None
    from database.models import Quartier

    distance = (
        db.query(func.ST_DistanceSphere(Quartier.geom, geom_point))
        .filter(Quartier.id == quartier_id, Quartier.geom.isnot(None))
        .scalar()
    )
    return float(distance) if distance is not None else None


@router.get("/", response_model=List[ContribuableResponse])
def get_contribuables(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    actif: Optional[bool] = None,
    collecteur_id: Optional[int] = None,
    quartier_id: Optional[int] = None,
    type_contribuable_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Récupère la liste des contribuables avec filtres et relations"""
    from sqlalchemy.orm import joinedload
    
    # Query de base avec relations (incluant la zone du quartier)
    from database.models import Quartier, Zone
    query = db.query(Contribuable).options(
        joinedload(Contribuable.type_contribuable),
        joinedload(Contribuable.quartier).joinedload(Quartier.zone),
        joinedload(Contribuable.collecteur)
    )
    
    # Query pour compter le total (sans les relations pour la performance)
    count_query = db.query(func.count(Contribuable.id))
    
    # Appliquer les mêmes filtres aux deux queries
    if actif is not None:
        query = query.filter(Contribuable.actif == actif)
        count_query = count_query.filter(Contribuable.actif == actif)
    if collecteur_id:
        query = query.filter(Contribuable.collecteur_id == collecteur_id)
        count_query = count_query.filter(Contribuable.collecteur_id == collecteur_id)
    if quartier_id:
        query = query.filter(Contribuable.quartier_id == quartier_id)
        count_query = count_query.filter(Contribuable.quartier_id == quartier_id)
    if type_contribuable_id:
        query = query.filter(Contribuable.type_contribuable_id == type_contribuable_id)
        count_query = count_query.filter(Contribuable.type_contribuable_id == type_contribuable_id)
    if search:
        search_term = f"%{search}%"
        search_filter = (
            (Contribuable.nom.ilike(search_term)) |
            (Contribuable.prenom.ilike(search_term)) |
            (Contribuable.telephone.ilike(search_term)) |
            (Contribuable.numero_identification.ilike(search_term))
        )
        query = query.filter(search_filter)
        count_query = count_query.filter(search_filter)
    
    # Récupérer les résultats
    contribuables = query.offset(skip).limit(limit).all()
    
    # Note: Le total n'est pas retourné dans la réponse car on utilise List[ContribuableResponse]
    # Pour avoir le total, il faudrait créer un schéma de réponse avec pagination
    # Pour l'instant, on retourne juste la liste
    return contribuables


@router.get("/{contribuable_id}", response_model=ContribuableResponse)
def get_contribuable(contribuable_id: int, db: Session = Depends(get_db)):
    """Récupère un contribuable par son ID avec toutes les relations"""
    from sqlalchemy.orm import joinedload
    from database.models import Quartier
    
    contribuable = db.query(Contribuable).options(
        joinedload(Contribuable.type_contribuable),
        joinedload(Contribuable.quartier).joinedload(Quartier.zone),
        joinedload(Contribuable.collecteur)
    ).filter(Contribuable.id == contribuable_id).first()
    
    if not contribuable:
        raise HTTPException(status_code=404, detail="Contribuable non trouvé")
    return contribuable


@router.post("/", response_model=ContribuableResponse, status_code=201)
def create_contribuable(contribuable: ContribuableCreate, db: Session = Depends(get_db)):
    """Crée un nouveau contribuable"""
    from sqlalchemy.orm import joinedload
    
    # Vérifier si le téléphone existe déjà
    existing = db.query(Contribuable).filter(Contribuable.telephone == contribuable.telephone).first()
    if existing:
        raise HTTPException(status_code=400, detail="Un contribuable avec ce téléphone existe déjà")
    
    # Vérifier si le numéro d'identification existe déjà (si fourni)
    if contribuable.numero_identification:
        existing_id = db.query(Contribuable).filter(Contribuable.numero_identification == contribuable.numero_identification).first()
        if existing_id:
            raise HTTPException(status_code=400, detail="Un contribuable avec ce numéro d'identification existe déjà")
    
    # Détection automatique de zone si GPS disponible
    quartier_id = contribuable.quartier_id
    geom_point = make_point(contribuable.longitude, contribuable.latitude)
    distance_m = None
    if geom_point is not None:
        auto_quartier_id, auto_distance = find_nearest_quartier(db, geom_point)
        if auto_quartier_id:
            quartier_id = auto_quartier_id
            distance_m = auto_distance
        if distance_m is None:
            distance_m = distance_to_quartier(db, quartier_id, geom_point)
    
    # Créer le contribuable avec le quartier_id (détecté ou fourni)
    contribuable_dict = contribuable.dict(exclude={'taxes_ids'})
    contribuable_dict['quartier_id'] = quartier_id
    db_contribuable = Contribuable(**contribuable_dict)
    if geom_point is not None:
        db_contribuable.geom = geom_point
    db_contribuable.distance_quartier_m = distance_m
    db.add(db_contribuable)
    db.commit()
    db.refresh(db_contribuable)
    
    # Créer les affectations de taxes si des taxes sont fournies
    if contribuable.taxes_ids and len(contribuable.taxes_ids) > 0:
        from database.models import AffectationTaxe, Taxe
        from datetime import datetime
        
        for taxe_id in contribuable.taxes_ids:
            # Vérifier que la taxe existe et est active
            taxe = db.query(Taxe).filter(Taxe.id == taxe_id, Taxe.actif == True).first()
            if taxe:
                # Vérifier si l'affectation existe déjà
                existing = db.query(AffectationTaxe).filter(
                    AffectationTaxe.contribuable_id == db_contribuable.id,
                    AffectationTaxe.taxe_id == taxe_id,
                    AffectationTaxe.actif == True
                ).first()
                
                if not existing:
                    affectation = AffectationTaxe(
                        contribuable_id=db_contribuable.id,
                        taxe_id=taxe_id,
                        date_debut=datetime.utcnow(),
                        date_fin=None,  # Toujours active par défaut
                        montant_custom=None if not taxe.montant_variable else None,  # Peut être défini plus tard
                        actif=True
                    )
                    db.add(affectation)
        
        db.commit()
    
    # Recharger avec les relations (incluant la zone du quartier)
    from database.models import Quartier
    db_contribuable = db.query(Contribuable).options(
        joinedload(Contribuable.type_contribuable),
        joinedload(Contribuable.quartier).joinedload(Quartier.zone),
        joinedload(Contribuable.collecteur)
    ).filter(Contribuable.id == db_contribuable.id).first()
    
    return db_contribuable


@router.put("/{contribuable_id}", response_model=ContribuableResponse)
def update_contribuable(contribuable_id: int, contribuable_update: ContribuableUpdate, db: Session = Depends(get_db)):
    """Met à jour un contribuable"""
    from sqlalchemy.orm import joinedload
    
    db_contribuable = db.query(Contribuable).filter(Contribuable.id == contribuable_id).first()
    if not db_contribuable:
        raise HTTPException(status_code=404, detail="Contribuable non trouvé")
    
    # Vérifier si le téléphone existe déjà (si modifié)
    if contribuable_update.telephone and contribuable_update.telephone != db_contribuable.telephone:
        existing = db.query(Contribuable).filter(Contribuable.telephone == contribuable_update.telephone).first()
        if existing:
            raise HTTPException(status_code=400, detail="Un contribuable avec ce téléphone existe déjà")
    
    # Vérifier si le numéro d'identification existe déjà (si modifié)
    if contribuable_update.numero_identification and contribuable_update.numero_identification != db_contribuable.numero_identification:
        existing_id = db.query(Contribuable).filter(Contribuable.numero_identification == contribuable_update.numero_identification).first()
        if existing_id:
            raise HTTPException(status_code=400, detail="Un contribuable avec ce numéro d'identification existe déjà")
    
    update_data = contribuable_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_contribuable, field, value)
    
    if "latitude" in update_data or "longitude" in update_data:
        geom_point = make_point(db_contribuable.longitude, db_contribuable.latitude)
        db_contribuable.geom = geom_point
        if geom_point is not None:
            auto_quartier_id, auto_distance = find_nearest_quartier(db, geom_point)
            if auto_quartier_id:
                db_contribuable.quartier_id = auto_quartier_id
                db_contribuable.distance_quartier_m = auto_distance
            else:
                db_contribuable.distance_quartier_m = distance_to_quartier(db, db_contribuable.quartier_id, geom_point)

    if "quartier_id" in update_data and db_contribuable.geom is not None:
        db_contribuable.distance_quartier_m = distance_to_quartier(db, db_contribuable.quartier_id, db_contribuable.geom)
    
    db_contribuable.updated_at = datetime.utcnow()
    db.commit()
    
    # Recharger avec les relations (incluant la zone du quartier)
    from sqlalchemy.orm import joinedload
    from database.models import Quartier
    db_contribuable = db.query(Contribuable).options(
        joinedload(Contribuable.type_contribuable),
        joinedload(Contribuable.quartier).joinedload(Quartier.zone),
        joinedload(Contribuable.collecteur)
    ).filter(Contribuable.id == contribuable_id).first()
    
    return db_contribuable


@router.patch("/{contribuable_id}/transfert", response_model=ContribuableResponse)
def transfert_contribuable(
    contribuable_id: int,
    nouveau_collecteur_id: int = Query(..., description="ID du nouveau collecteur"),
    db: Session = Depends(get_db)
):
    """Transfère un contribuable à un autre collecteur"""
    from sqlalchemy.orm import joinedload
    
    db_contribuable = db.query(Contribuable).filter(Contribuable.id == contribuable_id).first()
    if not db_contribuable:
        raise HTTPException(status_code=404, detail="Contribuable non trouvé")
    
    # Vérifier que le nouveau collecteur existe
    from database.models import Collecteur
    nouveau_collecteur = db.query(Collecteur).filter(Collecteur.id == nouveau_collecteur_id).first()
    if not nouveau_collecteur:
        raise HTTPException(status_code=404, detail="Collecteur non trouvé")
    
    if nouveau_collecteur.statut.value != 'active':
        raise HTTPException(status_code=400, detail="Le collecteur cible n'est pas actif")
    
    ancien_collecteur_id = db_contribuable.collecteur_id
    db_contribuable.collecteur_id = nouveau_collecteur_id
    db_contribuable.updated_at = datetime.utcnow()
    
    # TODO: Historiser le transfert
    
    db.commit()
    
    # Recharger avec les relations (incluant la zone du quartier)
    from sqlalchemy.orm import joinedload
    from database.models import Quartier
    db_contribuable = db.query(Contribuable).options(
        joinedload(Contribuable.type_contribuable),
        joinedload(Contribuable.quartier).joinedload(Quartier.zone),
        joinedload(Contribuable.collecteur)
    ).filter(Contribuable.id == contribuable_id).first()
    
    return db_contribuable


@router.delete("/{contribuable_id}", status_code=204)
def delete_contribuable(contribuable_id: int, db: Session = Depends(get_db)):
    """Supprime un contribuable (soft delete)"""
    db_contribuable = db.query(Contribuable).filter(Contribuable.id == contribuable_id).first()
    if not db_contribuable:
        raise HTTPException(status_code=404, detail="Contribuable non trouvé")
    
    db_contribuable.actif = False
    db_contribuable.updated_at = datetime.utcnow()
    db.commit()
    return None


@router.post("/{contribuable_id}/qr-code/generate")
def generate_qr_code_for_contribuable(
    contribuable_id: int,
    db: Session = Depends(get_db)
):
    """
    Génère un QR code pour un contribuable et le sauvegarde dans la base de données
    """
    contribuable = db.query(Contribuable).filter(Contribuable.id == contribuable_id).first()
    
    if not contribuable:
        raise HTTPException(status_code=404, detail="Contribuable non trouvé")
    
    # Générer un nouveau QR code si n'existe pas
    if not contribuable.qr_code:
        contribuable.qr_code = generate_qr_code_string(contribuable.id)
        contribuable.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(contribuable)
    
    return {
        "contribuable_id": contribuable.id,
        "qr_code": contribuable.qr_code,
        "message": "QR code généré avec succès"
    }


@router.get("/{contribuable_id}/qr-code/image")
def get_qr_code_image(
    contribuable_id: int,
    size: int = Query(300, ge=100, le=1000),
    with_details: bool = Query(False),
    db: Session = Depends(get_db)
):
    """
    Récupère l'image du QR code d'un contribuable
    """
    from sqlalchemy.orm import joinedload
    
    contribuable = db.query(Contribuable).options(
        joinedload(Contribuable.type_contribuable)
    ).filter(Contribuable.id == contribuable_id).first()
    
    if not contribuable:
        raise HTTPException(status_code=404, detail="Contribuable non trouvé")
    
    # Générer le QR code s'il n'existe pas
    if not contribuable.qr_code:
        contribuable.qr_code = generate_qr_code_string(contribuable.id)
        contribuable.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(contribuable)
    
    # Générer l'image
    if with_details:
        img_buffer = generate_qr_code_with_info(contribuable, size=size, include_details=True)
    else:
        img_buffer = generate_qr_code_image(contribuable.qr_code, size=size)
    
    return StreamingResponse(
        img_buffer,
        media_type="image/png",
        headers={
            "Content-Disposition": f'inline; filename="qr_code_{contribuable_id}.png"'
        }
    )


@router.get("/{contribuable_id}/qr-code/download")
def download_qr_code(
    contribuable_id: int,
    size: int = Query(400, ge=100, le=1000),
    with_details: bool = Query(True),
    db: Session = Depends(get_db)
):
    """
    Télécharge l'image du QR code d'un contribuable avec les détails
    """
    from sqlalchemy.orm import joinedload
    
    contribuable = db.query(Contribuable).options(
        joinedload(Contribuable.type_contribuable)
    ).filter(Contribuable.id == contribuable_id).first()
    
    if not contribuable:
        raise HTTPException(status_code=404, detail="Contribuable non trouvé")
    
    # Générer le QR code s'il n'existe pas
    if not contribuable.qr_code:
        contribuable.qr_code = generate_qr_code_string(contribuable.id)
        contribuable.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(contribuable)
    
    # Générer l'image avec détails
    img_buffer = generate_qr_code_with_info(contribuable, size=size, include_details=with_details)
    
    nom_complet = f"{contribuable.nom}_{contribuable.prenom or ''}".strip().replace(' ', '_')
    filename = f"QR_Code_{nom_complet}_{contribuable_id}.png"
    
    return StreamingResponse(
        img_buffer,
        media_type="image/png",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )

