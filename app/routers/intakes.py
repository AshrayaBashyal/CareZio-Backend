from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload
from datetime import datetime
from typing import List

from app.database import get_db
from app import schemas, models
from app.oauth2 import get_current_user

router = APIRouter(
    prefix="/intakes",
    tags=["Intakes"]
)

@router.post("/", response_model=schemas.MedicineIntakeWithMedicineOut)
def create_intake(intake: schemas.MedicineIntakeCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Log a medicine intake for the current user and decrement inventory.
    - `intake.medicine_id`: ID of the medicine being taken.
    """
    # Verify the medicine exists and belongs to the user
    medicine = db.query(models.Medicine).filter(
        models.Medicine.id == intake.medicine_id,
        models.Medicine.user_id == current_user.id
    ).first()
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found for this user")

    # Decrement inventory if available (but don't go below 0)
    if medicine.inventory is not None and medicine.inventory > 0:
        medicine.inventory -= 1

    new_intake = models.MedicineIntakeLog(
        medicine_id=intake.medicine_id,
        user_id=current_user.id,
        taken_at=datetime.now()  # will be overwritten by DB default if server_default used
    )
    db.add(new_intake)
    db.commit()
    db.refresh(new_intake)

    return {
        "id": new_intake.id,
        "medicine_id": new_intake.medicine_id,
        "taken_at": new_intake.taken_at,
        "medicine_name": medicine.name,
        "medicine_dosage": medicine.dosage
    }

@router.get("/", response_model=List[schemas.MedicineIntakeWithMedicineOut])
def get_intakes(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Retrieve medicine intake logs for the current user (most recent first).
    """
    intakes = db.query(models.MedicineIntakeLog).options(
        selectinload(models.MedicineIntakeLog.medicine)
    ).filter(
        models.MedicineIntakeLog.user_id == current_user.id
    ).order_by(models.MedicineIntakeLog.taken_at.desc()).all()

    res = []
    for intake in intakes:
        res.append({
            "id": intake.id,
            "medicine_id": intake.medicine_id,
            "taken_at": intake.taken_at,
            "medicine_name": intake.medicine.name if intake.medicine else None,
            "medicine_dosage": intake.medicine.dosage if intake.medicine else None
        })
    return res

@router.delete("/{intake_id}", status_code=204)
def delete_intake(intake_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Delete a medicine intake record by ID (for current user) and restore inventory.
    """
    intake = db.query(models.MedicineIntakeLog).filter(
        models.MedicineIntakeLog.id == intake_id,
        models.MedicineIntakeLog.user_id == current_user.id
    ).first()
    if not intake:
        raise HTTPException(status_code=404, detail="Intake not found or not authorized")

    # Restore inventory when deleting an intake record
    medicine = db.query(models.Medicine).filter(
        models.Medicine.id == intake.medicine_id
    ).first()
    if medicine:
        medicine.inventory = (medicine.inventory or 0) + 1

    db.delete(intake)
    db.commit()
    return None
