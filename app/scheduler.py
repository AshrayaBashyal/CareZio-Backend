from datetime import datetime, timezone
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session, selectinload

from app.database import SessionLocal
from app import models
from app.firebase import send_push_notification

"""
Background scheduler for medicine reminders and inventory alerts.
"""

scheduler = BackgroundScheduler()

def check_and_send_reminders():
    """
    Periodically checks schedules and inventory to create and send notifications.
    """
    db: Session = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        current_time = now.time().replace(second=0, microsecond=0)

        print(f"[Scheduler] Checking reminders at {now.isoformat()}")

        # ---------- Part 1: schedule-based reminders ----------
        schedules = db.query(models.MedicineSchedule).options(
            selectinload(models.MedicineSchedule.times),
            selectinload(models.MedicineSchedule.medicine)
        ).all()

        for schedule in schedules:
            medicine = schedule.medicine
            if not medicine:
                continue

            # Check each schedule time (ScheduleTime.time_of_day)
            for st in schedule.times:
                tod = st.time_of_day
                if tod.hour == current_time.hour and tod.minute == current_time.minute:
                    title = f"Time to take {medicine.name}"
                    message = f"Please take {medicine.name} ({medicine.dosage or 'dose'}) now."
                    notif = models.Notification(
                        user_id=medicine.user_id,
                        title=title,
                        message=message,
                        notification_type="reminder",
                        related_entity_type="medicine",
                        related_entity_id=medicine.id
                    )
                    db.add(notif)
                    db.commit()  # commit early to persist for reading fcm token
                    print(f"[Scheduler] Created reminder notification for user {medicine.user_id} - medicine {medicine.name}")

                    # Try to send push notification
                    user = db.query(models.User).filter(models.User.id == medicine.user_id).first()
                    if user and user.fcm_token:
                        send_push_notification(user.fcm_token, title, message)

        # ---------- Part 2: low-inventory check for ALL medicines ----------
        low_meds = db.query(models.Medicine).filter(
            models.Medicine.inventory.isnot(None),
            models.Medicine.low_threshold.isnot(None),
            models.Medicine.inventory <= models.Medicine.low_threshold
        ).all()

        for medicine in low_meds:
            # Avoid duplicate "inventory" notifications
            existing = db.query(models.Notification).filter(
                models.Notification.related_entity_type == "medicine",
                models.Notification.related_entity_id == medicine.id,
                models.Notification.notification_type == "inventory"
            ).first()

            if existing:
                continue  # skip if notification already exists

            title = f"Low stock: {medicine.name}"
            message = f"{medicine.name} running low — {medicine.inventory} left"
            notif = models.Notification(
                user_id=medicine.user_id,
                title=title,
                message=message,
                notification_type="inventory",
                related_entity_type="medicine",
                related_entity_id=medicine.id
            )
            db.add(notif)
            db.commit()
            print(f"[Scheduler] Low inventory alert created for medicine {medicine.name} (user {medicine.user_id})")

            # Send push notification
            user = db.query(models.User).filter(models.User.id == medicine.user_id).first()
            if user and user.fcm_token:
                send_push_notification(user.fcm_token, title, message)

    except Exception as e:
        print(f"[Scheduler ERROR] {e}")
        db.rollback()
    finally:
        db.close()

def start_scheduler():
    """
    Start the background scheduler for reminders (runs every 60 seconds).
    """
    # Run scheduler every 60 seconds. For testing, change seconds=10.
    scheduler.add_job(
        check_and_send_reminders,
        "interval",
        seconds=60,
        id="reminder_job",
        replace_existing=True
    )
    scheduler.start()
    print("[Scheduler] Started")
