"""
Routes pour la gestion des notifications
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import NotificationToken, Notification, Utilisateur
from schemas.notifications import (
    TokenRegister,
    TokenResponse,
    NotificationResponse,
    NotificationCreate,
    NotificationCountResponse
)
from auth.security import get_current_active_user
from datetime import datetime

router = APIRouter(
    prefix="/api/notifications",
    tags=["notifications"],
    dependencies=[Depends(get_current_active_user)],
)


@router.post("/register", response_model=TokenResponse, status_code=201)
def register_notification_token(
    token_data: TokenRegister,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_active_user),
):
    """
    Enregistrer le token FCM pour les notifications push
    """
    # Vérifier si le token existe déjà pour cet utilisateur
    existing_token = db.query(NotificationToken).filter(
        NotificationToken.token == token_data.token,
        NotificationToken.user_id == current_user.id
    ).first()
    
    if existing_token:
        # Mettre à jour
        existing_token.platform = token_data.platform
        existing_token.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing_token)
        return existing_token
    else:
        # Créer
        new_token = NotificationToken(
            user_id=current_user.id,
            token=token_data.token,
            platform=token_data.platform
        )
        db.add(new_token)
        db.commit()
        db.refresh(new_token)
        return new_token


@router.get("", response_model=list[NotificationResponse])
def get_notifications(
    unread_only: bool = Query(None, description="Filtrer uniquement les notifications non lues"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_active_user),
):
    """
    Récupérer les notifications de l'utilisateur
    """
    query = db.query(Notification).filter(
        Notification.user_id == current_user.id
    )
    
    if unread_only:
        query = query.filter(Notification.read == False)  # noqa: E712
    
    notifications = query.order_by(
        Notification.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return notifications


@router.put("/{notification_id}/read")
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_active_user),
):
    """
    Marquer une notification comme lue
    """
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification non trouvée")
    
    notification.read = True
    notification.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(notification)
    
    return {"id": notification.id, "read": notification.read, "updated_at": notification.updated_at}


@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_active_user),
):
    """
    Supprimer une notification
    """
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification non trouvée")
    
    db.delete(notification)
    db.commit()
    
    return {"message": "Notification supprimée avec succès"}


@router.get("/count", response_model=NotificationCountResponse)
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_active_user),
):
    """
    Obtenir le nombre de notifications non lues
    """
    count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.read == False  # noqa: E712
    ).count()
    
    return {"count": count}

