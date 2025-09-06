from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload
from typing import List

from app.database import get_db
from app import schemas, models
from app.oauth2 import get_current_user
from app.utils_time import local_time_to_nepal_timeobj, nepal_time_to_str

router = APIRouter(prefix="/schedules", tags=["Schedules"])

"""
Schedules router (Nepal-only time handling)

Overview
--------
This router manages medicine schedules for users.

Data model notes (fields used by these endpoints):
- MedicineSchedule:
    - id: primary key
    - medicine_id: references Medicine
    - frequency_type: string describing the frequency category (e.g. "daily", "weekly", "monthly") --- UNDER CONSTRUCTION-- WORKS AS DAILY ANY WAY
    - frequency_value: integer multiplier for the frequency_type (see examples below)  ---UNDER CONSTRUCTION---
    - created_at: timestamp when schedule was created
    - times: relationship to ScheduleTime entries

- ScheduleTime:
    - id: primary key
    - schedule_id: references MedicineSchedule
    - time_of_day: stored as a Python time object (NEPAL local time)

Important timezone policy
-------------------------
- All times handled by endpoints and stored in the database by this router are treated as
  Nepal local time (Asia/Kathmandu).
- Utility functions used:
    - local_time_to_nepal_timeobj(local_time): converts a string like "14:30" or a time object
      into a Nepal-local time object to store in the DB.
    - nepal_time_to_str(time_obj): returns "HH:MM:SS" string for the stored Nepal-local time.

Frequency fields explanation (precise behavior)
----------------------------------------------
- frequency_type (string):
    - Semantic category of the schedule (examples: "daily", "weekly", "monthly").
    - This is NOT a free-form string in practice; prefer the above categories for clarity.

- frequency_value (integer):
    - Multiplies the frequency_type (i.e., frequency_value = N means "every N <frequency_type>").
    - Examples:
        - frequency_type = "daily", frequency_value = 1  -> Every day
        - frequency_type = "daily", frequency_value = 3  -> Every 3 days
        - frequency_type = "weekly", frequency_value = 1 -> Every week
        - frequency_type = "weekly", frequency_value = 2 -> Every 2 weeks
- IMPORTANT: The current backend stores and returns these values but the scheduler logic
  (notification delivery) in `app/scheduler.py` may not enforce skipping days/weeks based on
  frequency_value. That means creating a schedule with frequency_type="daily", frequency_value=3
  will store "every 3 days" in the DB, but you must confirm scheduler enforcement if you need
  strict every-N-days behavior. (No code changes were made here; this note is for clarity.)

Payload examples
----------------
- Create schedule payload (example body for the POST /schedules endpoint):
{
  "frequency_type": "daily",
  "frequency_value": 1,
  "times": [
    {"time_of_day": "20:00"},
    {"time_of_day": "08:00"}
  ]
}
- Returned schedule times are strings in "HH:MM:SS" format representing Nepal local time.

Response shape
--------------
The endpoints return schedules with nested medicine info and times. Example:
{
  "id": 1,
  "frequency_type": "daily",
  "frequency_value": 1,
  "created_at": "2025-09-06T20:00:30.558597+05:45",
  "medicine": { ... },
  "times": [
    {"id": 1, "time_of_day": "20:01:00"}
  ]
}
"""

# ---------- Create schedule ----------
@router.post("/", response_model=schemas.MedicineScheduleWithMedicineOut)
def create_schedule(
        medicine_id: int,
        schedule_data: schemas.MedicineScheduleCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    """
    Create a medicine schedule for the current user.

    Behavior & expectations:
    - `medicine_id`: ID of an existing medicine that belongs to the current user.
    - `schedule_data.frequency_type`: e.g., "daily", "weekly", "monthly".
    - `schedule_data.frequency_value`: integer multiplier for the frequency_type (see module doc).
    - `schedule_data.times`: list of times (strings "HH:MM" or "HH:MM:SS" OR time objects).
      These are interpreted as Nepal local times and stored as Nepal-local time objects.

    Example request (JSON body):
    {
      "frequency_type": "daily",
      "frequency_value": 1,
      "times": [{"time_of_day": "20:00"}, {"time_of_day": "08:00"}]
    }

    Returns:
    - The created schedule object with nested medicine and times.
    """
    # Verify medicine exists and belongs to user
    medicine = db.query(models.Medicine).filter(
        models.Medicine.id == medicine_id,
        models.Medicine.user_id == current_user.id
    ).first()
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")

    # Create schedule
    schedule = models.MedicineSchedule(
        medicine_id=medicine.id,
        frequency_type=schedule_data.frequency_type,
        frequency_value=schedule_data.frequency_value
    )
    db.add(schedule)
    db.commit()
    db.refresh(schedule)

    # Store times directly as Nepal local time
    for time_data in schedule_data.times:
        nepal_time_obj = local_time_to_nepal_timeobj(time_data.time_of_day)
        schedule_time = models.ScheduleTime(
            schedule_id=schedule.id,
            time_of_day=nepal_time_obj
        )
        db.add(schedule_time)

    db.commit()

    # Refresh with relationships
    schedule = db.query(models.MedicineSchedule).options(
        selectinload(models.MedicineSchedule.medicine),
        selectinload(models.MedicineSchedule.times)
    ).filter(models.MedicineSchedule.id == schedule.id).first()

    # Build response converting stored times to string
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
            {"id": t.id, "time_of_day": nepal_time_to_str(t.time_of_day)}
            for t in schedule.times
        ]
    }

    return resp

# ---------- Get schedules for a specific medicine ----------
@router.get("/medicine/{medicine_id}", response_model=List[schemas.MedicineScheduleWithMedicineOut])
def get_schedules_for_medicine(
        medicine_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    """
    Get all schedules for a specific medicine of the current user.

    Returns schedule entries (with nested medicine info and times).
    All `time_of_day` values are returned as Nepal local time strings "HH:MM:SS".
    """
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
                {"id": t.id, "time_of_day": nepal_time_to_str(t.time_of_day)}
                for t in schedule.times
            ]
        })
    return out

# ---------- Get all schedules ----------
@router.get("/", response_model=List[schemas.MedicineScheduleWithMedicineOut])
def get_all_schedules(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    """
    Get all medicine schedules for the current user.

    Useful for listing and display in the UI. Times are Nepal local times.
    """
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
                {"id": t.id, "time_of_day": nepal_time_to_str(t.time_of_day)}
                for t in schedule.times
            ]
        })
    return out

# ---------- Get a single schedule ----------
@router.get("/{schedule_id}", response_model=schemas.MedicineScheduleWithMedicineOut)
def get_schedule(
        schedule_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    """
    Retrieve a specific schedule by ID for the current user.

    Returns the schedule and its times; all times are Nepal local time strings.
    """
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
            {"id": t.id, "time_of_day": nepal_time_to_str(t.time_of_day)}
            for t in schedule.times
        ]
    }
    return resp

# ---------- Update schedule ----------
@router.put("/{schedule_id}", response_model=schemas.MedicineScheduleWithMedicineOut)
def update_schedule(
        schedule_id: int,
        schedule_update: schemas.MedicineScheduleUpdate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    """
    Update an existing schedule (frequency or times) for the current user.

    - Provide `frequency_type` / `frequency_value` to change frequency metadata.
    - Provide `times` as Nepal local times (strings or time objects). All times stored as Nepal time.
    """
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
        # add new times as Nepal local time
        for time_data in schedule_update.times:
            nepal_time_obj = local_time_to_nepal_timeobj(time_data.time_of_day)
            schedule_time = models.ScheduleTime(schedule_id=schedule.id, time_of_day=nepal_time_obj)
            db.add(schedule_time)

    db.commit()

    # Refresh and return
    schedule = db.query(models.MedicineSchedule).options(
        selectinload(models.MedicineSchedule.medicine),
        selectinload(models.MedicineSchedule.times)
    ).filter(models.MedicineSchedule.id == schedule_id).first()

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
            {"id": t.id, "time_of_day": nepal_time_to_str(t.time_of_day)}
            for t in schedule.times
        ]
    }
    return resp

# ---------- Delete schedule ----------
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
