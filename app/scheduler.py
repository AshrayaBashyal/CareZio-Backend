from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session, selectinload
from zoneinfo import ZoneInfo

from app.database import SessionLocal
from app import models
from app.firebase import send_push_notification
from app.utils_time import local_time_to_nepal_timeobj, nepal_time_to_str

NEPAL_TZ = ZoneInfo("Asia/Kathmandu")

scheduler = BackgroundScheduler()

def check_and_send_reminders():
    """
    Periodically checks medicine schedules and inventory.
    All times are strictly Nepal local time.
    """
    db: Session = SessionLocal()
    try:
        now = datetime.now(NEPAL_TZ)
        current_time = now.time().replace(second=0, microsecond=0)

        print(f"[Scheduler] Checking reminders at Nepal time {now.isoformat()}")

        # ---------- Schedule-based reminders ----------
        schedules = db.query(models.MedicineSchedule).options(
            selectinload(models.MedicineSchedule.times),
            selectinload(models.MedicineSchedule.medicine)
        ).all()

        for schedule in schedules:
            medicine = schedule.medicine
            if not medicine:
                continue

            for st in schedule.times:
                tod = st.time_of_day

                if tod.hour == current_time.hour and tod.minute == current_time.minute:
                    # Check for existing reminder for this medicine at this time
                    existing_reminder = db.query(models.Notification).filter(
                        models.Notification.related_entity_type == "medicine",
                        models.Notification.related_entity_id == medicine.id,
                        models.Notification.notification_type == "reminder",
                        models.Notification.created_at >= datetime(
                            now.year, now.month, now.day, tod.hour, tod.minute, 0, tzinfo=NEPAL_TZ
                        )
                    ).first()

                    if existing_reminder:
                        continue  # Skip creating duplicate

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
                    db.commit()

                    user = db.query(models.User).filter(models.User.id == medicine.user_id).first()
                    if user:
                        for token_obj in user.fcm_tokens:
                            send_push_notification(token_obj.fcm_token, title, message)
                    print(f"[Scheduler] Reminder created for user {medicine.user_id} - medicine {medicine.name}")

        # ---------- Low-inventory check ----------
        low_meds = db.query(models.Medicine).filter(
            models.Medicine.inventory.isnot(None),
            models.Medicine.low_threshold.isnot(None),
            models.Medicine.inventory <= models.Medicine.low_threshold
        ).all()

        for medicine in low_meds:
            existing = db.query(models.Notification).filter(
                models.Notification.related_entity_type == "medicine",
                models.Notification.related_entity_id == medicine.id,
                models.Notification.notification_type == "inventory"
            ).first()
            if existing:
                continue

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

            user = db.query(models.User).filter(models.User.id == medicine.user_id).first()
            if user:
                for token_obj in user.fcm_tokens:
                    send_push_notification(token_obj.fcm_token, title, message)
            print(f"[Scheduler] Low inventory alert for medicine {medicine.name} (user {medicine.user_id})")

    except Exception as e:
        print(f"[Scheduler ERROR] {e}")
        db.rollback()
    finally:
        db.close()

def start_scheduler():
    """
    Start background scheduler (Nepal time, every 60 seconds).
    """
    scheduler.add_job(
        check_and_send_reminders,
        "interval",
        seconds=60,
        id="reminder_job",
        replace_existing=True
    )
    scheduler.start()
    print("[Scheduler] Started (Nepal time)")
