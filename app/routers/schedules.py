from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, selectinload
from typing import List, Optional

from app.database import get_db
from app import schemas, models
from app.oauth2 import get_current_user
from app.utils_time import local_time_to_utc_timeobj, utc_time_to_local_str

router = APIRouter(prefix="/schedules", tags=["Schedules"])

DEFAULT_TZ = "Asia/Kathmandu"  # fallback timezone if none provided

# ---------- Create schedule ----------
@router.post("/", response_model=schemas.MedicineScheduleWithMedicineOut)
def create_schedule(
        medicine_id: int,
        schedule_data: schemas.MedicineScheduleCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user),
        tz: Optional[str] = Query(None, description="Timezone of the provided times (e.g. 'Asia/Kathmandu'). If omitted, user.timezone (if present) or Asia/Kathmandu is used.")
):
    """
    Create a medicine schedule for the current user.
    - `medicine_id`: ID of the medicine to schedule.
    - `schedule_data.times`: list of local times (strings "HH:MM" or "HH:MM:SS") in user's timezone.
    - `frequency_type`: "daily" or "every_n_days".
    - `frequency_value`: number of days if `frequency_type` is "every_n_days".
    Times are converted to UTC for storage.
    """
    # determine timezone to use (preference: query tz -> user.timezone -> DEFAULT_TZ)
    user_tz = tz or getattr(current_user, "timezone", None) or DEFAULT_TZ

    # Verify medicine exists and belongs to user
    medicine = db.query(models.Medicine).filter(
        models.Medicine.id == medicine_id,
        models.Medicine.user_id == current_user.id
    ).first()
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")

    # Create schedule (main row)
    schedule = models.MedicineSchedule(
        medicine_id=medicine.id,
        frequency_type=schedule_data.frequency_type,
        frequency_value=schedule_data.frequency_value
    )
    db.add(schedule)
    db.commit()
    db.refresh(schedule)

    # Convert each provided local time to UTC time object and store
    for time_data in schedule_data.times:
        # time_data.time_of_day is a time object or string; convert it assuming user_tz
        utc_time_obj = local_time_to_utc_timeobj(time_data.time_of_day, user_tz)
        schedule_time = models.ScheduleTime(
            schedule_id=schedule.id,
            time_of_day=utc_time_obj
        )
        db.add(schedule_time)

    db.commit()

    # Refresh with relationships
    schedule = db.query(models.MedicineSchedule).options(
        selectinload(models.MedicineSchedule.medicine),
        selectinload(models.MedicineSchedule.times)
    ).filter(models.MedicineSchedule.id == schedule.id).first()

    # Build response converting stored UTC times back to user's local timezone for readability
    resp = {
        "id": schedule.id,
        "frequency_type": schedule.frequency_type,
        "frequency_value": schedule.frequency_value,
        "created_at": schedule.created_at,
        "medicine": {
            "id": schedule.medicine.id,
            "name": schedule.medicine.name,
            "dosage": schedule.medicine.dosage,
            "inventory": schedule.medicine.inventory,
            "low_threshold": schedule.medicine.low_threshold
        },
        "times": [
            {
                "id": t.id,
                # convert stored UTC t.time_of_day -> local string
                "time_of_day": utc_time_to_local_str(t.time_of_day, user_tz)
            }
            for t in schedule.times
        ]
    }

    return resp

@router.get("/medicine/{medicine_id}", response_model=List[schemas.MedicineScheduleWithMedicineOut])
def get_schedules_for_medicine(
        medicine_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user),
        tz: Optional[str] = Query(None, description="Timezone for returned times (e.g. 'Asia/Kathmandu')"),
):
    """
    Get all schedules for a specific medicine of the current user.
    Times are returned adjusted to the specified or user's timezone.
    """
    user_tz = tz or getattr(current_user, "timezone", None) or DEFAULT_TZ

    schedules = db.query(models.MedicineSchedule).options(
        selectinload(models.MedicineSchedule.medicine),
        selectinload(models.MedicineSchedule.times)
    ).join(models.Medicine).filter(
        models.Medicine.id == medicine_id,
        models.Medicine.user_id == current_user.id
    ).all()

    out = []
    for schedule in schedules:
        out.append({
            "id": schedule.id,
            "frequency_type": schedule.frequency_type,
            "frequency_value": schedule.frequency_value,
            "created_at": schedule.created_at,
            "medicine": {
                "id": schedule.medicine.id,
                "name": schedule.medicine.name,
                "dosage": schedule.medicine.dosage,
                "inventory": schedule.medicine.inventory,
                "low_threshold": schedule.medicine.low_threshold
            },
            "times": [
                {"id": t.id, "time_of_day": utc_time_to_local_str(t.time_of_day, user_tz)}
                for t in schedule.times
            ]
        })
    return out

@router.get("/", response_model=List[schemas.MedicineScheduleWithMedicineOut])
def get_all_schedules(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user),
        tz: Optional[str] = Query(None, description="Timezone for returned times (e.g. 'Asia/Kathmandu')"),
):
    """
    Get all medicine schedules for the current user.
    Times are returned adjusted to the specified or user's timezone.
    """
    user_tz = tz or getattr(current_user, "timezone", None) or DEFAULT_TZ

    schedules = db.query(models.MedicineSchedule).options(
        selectinload(models.MedicineSchedule.medicine),
        selectinload(models.MedicineSchedule.times)
    ).join(models.Medicine).filter(
        models.Medicine.user_id == current_user.id
    ).all()

    out = []
    for schedule in schedules:
        out.append({
            "id": schedule.id,
            "frequency_type": schedule.frequency_type,
            "frequency_value": schedule.frequency_value,
            "created_at": schedule.created_at,
            "medicine": {
                "id": schedule.medicine.id,
                "name": schedule.medicine.name,
                "dosage": schedule.medicine.dosage,
                "inventory": schedule.medicine.inventory,
                "low_threshold": schedule.medicine.low_threshold
            },
            "times": [
                {"id": t.id, "time_of_day": utc_time_to_local_str(t.time_of_day, user_tz)}
                for t in schedule.times
            ]
        })
    return out

@router.get("/{schedule_id}", response_model=schemas.MedicineScheduleWithMedicineOut)
def get_schedule(
        schedule_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user),
        tz: Optional[str] = Query(None, description="Timezone for returned times (e.g. 'Asia/Kathmandu')"),
):
    """
    Retrieve a specific schedule by ID for the current user.
    Times are returned adjusted to the specified or user's timezone.
    """
    user_tz = tz or getattr(current_user, "timezone", None) or DEFAULT_TZ

    schedule = db.query(models.MedicineSchedule).options(
        selectinload(models.MedicineSchedule.medicine),
        selectinload(models.MedicineSchedule.times)
    ).join(models.Medicine).filter(
        models.MedicineSchedule.id == schedule_id,
        models.Medicine.user_id == current_user.id
    ).first()

    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    resp = {
        "id": schedule.id,
        "frequency_type": schedule.frequency_type,
        "frequency_value": schedule.frequency_value,
        "created_at": schedule.created_at,
        "medicine": {
            "id": schedule.medicine.id,
            "name": schedule.medicine.name,
            "dosage": schedule.medicine.dosage,
            "inventory": schedule.medicine.inventory,
            "low_threshold": schedule.medicine.low_threshold
        },
        "times": [
            {"id": t.id, "time_of_day": utc_time_to_local_str(t.time_of_day, user_tz)}
            for t in schedule.times
        ]
    }
    return resp

@router.put("/{schedule_id}", response_model=schemas.MedicineScheduleWithMedicineOut)
def update_schedule(
        schedule_id: int,
        schedule_update: schemas.MedicineScheduleUpdate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user),
        tz: Optional[str] = Query(None, description="Timezone of provided times (e.g. 'Asia/Kathmandu').")
):
    """
    Update an existing schedule (frequency or times) for the current user.
    Provide times in local timezone to be converted to UTC.
    """
    user_tz = tz or getattr(current_user, "timezone", None) or DEFAULT_TZ

    schedule = db.query(models.MedicineSchedule).options(
        selectinload(models.MedicineSchedule.medicine),
        selectinload(models.MedicineSchedule.times)
    ).join(models.Medicine).filter(
        models.MedicineSchedule.id == schedule_id,
        models.Medicine.user_id == current_user.id
    ).first()

    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    if schedule_update.frequency_type is not None:
        schedule.frequency_type = schedule_update.frequency_type
    if schedule_update.frequency_value is not None:
        schedule.frequency_value = schedule_update.frequency_value

    if schedule_update.times is not None:
        # remove existing times
        db.query(models.ScheduleTime).filter(models.ScheduleTime.schedule_id == schedule.id).delete()
        # add new times (convert to UTC first)
        for time_data in schedule_update.times:
            utc_time_obj = local_time_to_utc_timeobj(time_data.time_of_day, user_tz)
            schedule_time = models.ScheduleTime(schedule_id=schedule.id, time_of_day=utc_time_obj)
            db.add(schedule_time)

    db.commit()

    schedule = db.query(models.MedicineSchedule).options(
        selectinload(models.MedicineSchedule.medicine),
        selectinload(models.MedicineSchedule.times)
    ).filter(models.MedicineSchedule.id == schedule_id).first()

    # return converted response
    resp = {
        "id": schedule.id,
        "frequency_type": schedule.frequency_type,
        "frequency_value": schedule.frequency_value,
        "created_at": schedule.created_at,
        "medicine": {
            "id": schedule.medicine.id,
            "name": schedule.medicine.name,
            "dosage": schedule.medicine.dosage,
            "inventory": schedule.medicine.inventory,
            "low_threshold": schedule.medicine.low_threshold
        },
        "times": [
            {"id": t.id, "time_of_day": utc_time_to_local_str(t.time_of_day, user_tz)}
            for t in schedule.times
        ]
    }
    return resp

@router.delete("/{schedule_id}")
def delete_schedule(schedule_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Delete a schedule by ID for the current user.
    """
    schedule = db.query(models.MedicineSchedule).join(models.Medicine).filter(
        models.MedicineSchedule.id == schedule_id,
        models.Medicine.user_id == current_user.id
    ).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    db.delete(schedule)
    db.commit()
    return {"message": "Schedule deleted successfully"}
