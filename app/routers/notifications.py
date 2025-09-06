from fastapi import APIRouter, Depends, HTTPException, Body, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app import models, schemas
from app.database import get_db
from app.oauth2 import get_current_user
from app.firebase import send_push_to_user

router = APIRouter(prefix="/notifications", tags=["Notifications"])


# -------------------------------
# Register FCM Token
# -------------------------------
@router.post("/register-token")
def register_fcm_token(
    token: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Register a Firebase Cloud Messaging (FCM) token for the current user.
    - Allows multiple tokens per user.
    - Same token can belong to multiple users (multi-account device).
    """
    existing = (
        db.query(models.UserFCMToken)
        .filter(
            models.UserFCMToken.user_id == current_user.id,
            models.UserFCMToken.fcm_token == token,
        )
        .first()
    )

    if existing:
        return {"message": "Token already registered"}

    new_token = models.UserFCMToken(user_id=current_user.id, fcm_token=token)
    db.add(new_token)
    db.commit()
    db.refresh(new_token)

    return {"message": "FCM token registered successfully", "token_id": new_token.id}


# -------------------------------
# Create Notification
# -------------------------------
@router.post("/", response_model=schemas.NotificationOut)
def create_notification(
    notification: schemas.NotificationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    For Testing/ Future Use --> Doctors can send notification to user
    Create a new notification for the current user.
    Also sends push notifications to all registered devices of this user.
    """
    db_notification = models.Notification(
        user_id=current_user.id,
        title=notification.title,
        message=notification.message,
        notification_type=notification.notification_type,
        related_entity_type=notification.related_entity_type,
        related_entity_id=notification.related_entity_id,
    )
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)

    # 🔔 Trigger push notifications
    send_push_to_user(db, current_user.id, db_notification.title, db_notification.message)

    return db_notification


# -------------------------------
# Get Notifications with Filters
# -------------------------------
@router.get("/", response_model=List[schemas.NotificationOut])
def get_notifications(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    unread_only: bool = Query(False, description="Filter for unread notifications only"),
    notification_type: Optional[str] = Query(None, description="Filter by notification type (e.g. 'reminder', 'inventory', 'system')"),
):
    """
    Retrieve notifications for the current user with optional filters.
    """
    query = db.query(models.Notification).filter(models.Notification.user_id == current_user.id)

    if unread_only:
        query = query.filter(models.Notification.is_read == False)

    if notification_type:
        query = query.filter(models.Notification.notification_type == notification_type)

    notifications = query.order_by(models.Notification.created_at.desc()).offset(skip).limit(limit).all()
    return notifications


# -------------------------------
# Get Single Notification
# -------------------------------
@router.get("/{notification_id}", response_model=schemas.NotificationOut)
def get_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Retrieve a specific notification by ID for the current user.
    """
    notification = (
        db.query(models.Notification)
        .filter(models.Notification.id == notification_id, models.Notification.user_id == current_user.id)
        .first()
    )
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification


# -------------------------------
# Update Notification (mark read/unread)
# -------------------------------
@router.patch("/{notification_id}", response_model=schemas.NotificationOut)
def update_notification(
    notification_id: int,
    update_data: schemas.NotificationUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Update a notification (mark as read/unread) for the current user.
    """
    notification = (
        db.query(models.Notification)
        .filter(models.Notification.id == notification_id, models.Notification.user_id == current_user.id)
        .first()
    )
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    if update_data.is_read is not None:
        notification.is_read = update_data.is_read

    db.commit()
    db.refresh(notification)
    return notification


# -------------------------------
# Mark All Notifications Read
# -------------------------------
@router.post("/mark-all-read")
def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Mark all unread notifications as read for the current user.
    """
    db.query(models.Notification).filter(
        models.Notification.user_id == current_user.id, models.Notification.is_read == False
    ).update({"is_read": True})
    db.commit()
    return {"message": "All notifications marked as read"}


# -------------------------------
# Delete Notification
# -------------------------------
@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Delete a notification by ID for the current user.
    """
    notification = (
        db.query(models.Notification)
        .filter(models.Notification.id == notification_id, models.Notification.user_id == current_user.id)
        .first()
    )
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    db.delete(notification)
    db.commit()
    return {"message": "Notification deleted successfully"}


# -------------------------------
# Notification Statistics
# -------------------------------
@router.get("/stats/overview")
def get_notification_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Get notification statistics for the current user (total/unread count and breakdown by type).
    """
    total = db.query(models.Notification).filter(models.Notification.user_id == current_user.id).count()
    unread = (
        db.query(models.Notification)
        .filter(models.Notification.user_id == current_user.id, models.Notification.is_read == False)
        .count()
    )

    by_type = {}
    types = (
        db.query(models.Notification.notification_type, models.Notification.is_read)
        .filter(models.Notification.user_id == current_user.id)
        .all()
    )
    for notif_type, is_read in types:
        if notif_type not in by_type:
            by_type[notif_type] = {"total": 0, "unread": 0}
        by_type[notif_type]["total"] += 1
        if not is_read:
            by_type[notif_type]["unread"] += 1

    return {"total": total, "unread": unread, "by_type": by_type}
