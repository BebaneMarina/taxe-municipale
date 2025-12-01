"""
Routes pour la gestion complète des utilisateurs
CRUD complet avec gestion des rôles et permissions
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, List
from datetime import datetime

from database.database import get_db
from database.models import Utilisateur, RoleEnum
from routers.parametrage import RoleParametrage
from auth.security import (
    get_current_active_user,
    get_password_hash,
    require_role
)
from auth.schemas import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponse
)

router = APIRouter(prefix="/api/utilisateurs", tags=["utilisateurs"])


def check_admin_permission(current_user: Utilisateur):
    """Vérifie que l'utilisateur est admin"""
    if current_user.role != RoleEnum.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les administrateurs peuvent effectuer cette action"
        )


@router.get("", response_model=UserListResponse)
def list_utilisateurs(
    skip: int = Query(0, ge=0, description="Nombre d'éléments à sauter"),
    limit: int = Query(100, ge=1, le=1000, description="Nombre d'éléments à retourner"),
    search: Optional[str] = Query(None, description="Recherche par nom, prénom ou email"),
    role: Optional[str] = Query(None, description="Filtrer par rôle"),
    actif: Optional[bool] = Query(None, description="Filtrer par statut actif/inactif"),
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_active_user)
):
    """
    Liste tous les utilisateurs avec pagination et filtres.
    Accessible par tous les utilisateurs authentifiés.
    """
    query = db.query(Utilisateur)
    
    # Filtre de recherche
    if search:
        search_term = f"%{search.lower()}%"
        query = query.filter(
            or_(
                Utilisateur.nom.ilike(search_term),
                Utilisateur.prenom.ilike(search_term),
                Utilisateur.email.ilike(search_term)
            )
        )
    
    # Filtre par rôle
    if role:
        valid_roles = [r.value for r in RoleEnum]
        if role not in valid_roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Rôle invalide. Rôles valides: {', '.join(valid_roles)}"
            )
        query = query.filter(Utilisateur.role == role)
    
    # Filtre par statut actif
    if actif is not None:
        query = query.filter(Utilisateur.actif == actif)
    
    # Compter le total
    total = query.count()
    
    # Pagination
    utilisateurs = query.order_by(Utilisateur.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "items": utilisateurs,
        "skip": skip,
        "limit": limit
    }


@router.get("/{user_id}", response_model=UserResponse)
def get_utilisateur(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_active_user)
):
    """
    Récupère les détails d'un utilisateur spécifique.
    Accessible par tous les utilisateurs authentifiés.
    """
    utilisateur = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
    
    if not utilisateur:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    return utilisateur


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_utilisateur(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_active_user)
):
    """
    Crée un nouvel utilisateur.
    Seuls les administrateurs peuvent créer des utilisateurs.
    """
    check_admin_permission(current_user)
    
    # Vérifier si l'email existe déjà
    existing_user = db.query(Utilisateur).filter(Utilisateur.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un utilisateur avec cet email existe déjà"
        )
    
    # Vérifier si le téléphone existe déjà (si fourni)
    if user_data.telephone:
        existing_phone = db.query(Utilisateur).filter(
            Utilisateur.telephone == user_data.telephone
        ).first()
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Un utilisateur avec ce numéro de téléphone existe déjà"
            )
    
    # Vérifier si le rôle existe dans la table role, sinon le créer automatiquement
    role_code = user_data.role
    existing_role = db.query(RoleParametrage).filter(
        RoleParametrage.code == role_code
    ).first()
    
    if not existing_role:
        # Créer le rôle automatiquement
        role_nom = role_code.replace('_', ' ').title()
        new_role = RoleParametrage(
            nom=role_nom,
            code=role_code,
            description=f"Rôle {role_nom} créé automatiquement",
            permissions="[]",  # Permissions vides par défaut
            actif=True
        )
        db.add(new_role)
        db.flush()  # Flush pour obtenir l'ID sans commit
        print(f"Rôle créé automatiquement: {role_code}")
    
    # Créer l'utilisateur
    hashed_password = get_password_hash(user_data.password)
    db_user = Utilisateur(
        nom=user_data.nom,
        prenom=user_data.prenom,
        email=user_data.email,
        telephone=user_data.telephone,
        mot_de_passe_hash=hashed_password,
        role=user_data.role,
        actif=True
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.put("/{user_id}", response_model=UserResponse)
def update_utilisateur(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_active_user)
):
    """
    Met à jour un utilisateur.
    - Les administrateurs peuvent modifier tous les utilisateurs
    - Les utilisateurs peuvent modifier leurs propres informations (sauf le rôle)
    """
    utilisateur = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
    
    if not utilisateur:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    # Vérifier les permissions
    is_admin = current_user.role == RoleEnum.ADMIN.value
    is_self = current_user.id == user_id
    
    if not is_admin and not is_self:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez modifier que votre propre profil"
        )
    
    # Si ce n'est pas un admin, empêcher la modification du rôle et du statut actif
    if not is_admin:
        if user_update.role is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vous ne pouvez pas modifier votre propre rôle"
            )
        if user_update.actif is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vous ne pouvez pas modifier votre propre statut actif"
            )
    
    # Vérifier l'unicité de l'email si modifié
    if user_update.email and user_update.email != utilisateur.email:
        existing_email = db.query(Utilisateur).filter(
            Utilisateur.email == user_update.email,
            Utilisateur.id != user_id
        ).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Un utilisateur avec cet email existe déjà"
            )
    
    # Vérifier l'unicité du téléphone si modifié
    if user_update.telephone and user_update.telephone != utilisateur.telephone:
        existing_phone = db.query(Utilisateur).filter(
            Utilisateur.telephone == user_update.telephone,
            Utilisateur.id != user_id
        ).first()
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Un utilisateur avec ce numéro de téléphone existe déjà"
            )
    
    # Mettre à jour les champs
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(utilisateur, field, value)
    
    utilisateur.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(utilisateur)
    
    return utilisateur


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_utilisateur(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_active_user)
):
    """
    Supprime un utilisateur.
    Seuls les administrateurs peuvent supprimer des utilisateurs.
    Un utilisateur ne peut pas se supprimer lui-même.
    """
    check_admin_permission(current_user)
    
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous ne pouvez pas supprimer votre propre compte"
        )
    
    utilisateur = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
    
    if not utilisateur:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    db.delete(utilisateur)
    db.commit()
    
    return None


@router.patch("/{user_id}/activate", response_model=UserResponse)
def activate_utilisateur(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_active_user)
):
    """
    Active un utilisateur.
    Seuls les administrateurs peuvent activer/désactiver des utilisateurs.
    """
    check_admin_permission(current_user)
    
    utilisateur = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
    
    if not utilisateur:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    utilisateur.actif = True
    utilisateur.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(utilisateur)
    
    return utilisateur


@router.patch("/{user_id}/deactivate", response_model=UserResponse)
def deactivate_utilisateur(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_active_user)
):
    """
    Désactive un utilisateur.
    Seuls les administrateurs peuvent activer/désactiver des utilisateurs.
    Un administrateur ne peut pas se désactiver lui-même.
    """
    check_admin_permission(current_user)
    
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous ne pouvez pas désactiver votre propre compte"
        )
    
    utilisateur = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
    
    if not utilisateur:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    utilisateur.actif = False
    utilisateur.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(utilisateur)
    
    return utilisateur


@router.get("/roles/list", response_model=List[dict])
def list_roles(
    current_user: Utilisateur = Depends(get_current_active_user)
):
    """
    Liste tous les rôles disponibles.
    Accessible par tous les utilisateurs authentifiés.
    """
    roles = [
        {
            "value": role.value,
            "label": role.value.replace("_", " ").title()
        }
        for role in RoleEnum
    ]
    return roles

