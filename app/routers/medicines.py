from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database import get_db
from app.oauth2 import get_current_user

router = APIRouter(prefix="/medicines", tags=["Medicines"])

# Create
@router.post("/", response_model=schemas.MedicineOut)
def create_medicine(med: schemas.MedicineCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Create a new medicine in user's inventory.
    """
    medicine = models.Medicine(**med.dict(), user_id=current_user.id)
    db.add(medicine)
    db.commit()
    db.refresh(medicine)
    return medicine

# Read all
@router.get("/", response_model=List[schemas.MedicineOut])
def get_medicines(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Retrieve all medicines for the current user.
    """
    return db.query(models.Medicine).filter(models.Medicine.user_id == current_user.id).all()

# Update
@router.put("/{medicine_id}", response_model=schemas.MedicineOut)
def update_medicine(medicine_id: int, med_update: schemas.MedicineCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Update an existing medicine's details for the current user.
    """
    med = db.query(models.Medicine).filter(models.Medicine.id == medicine_id, models.Medicine.user_id == current_user.id).first()
    if not med:
        raise HTTPException(status_code=404, detail="Medicine not found")
    for key, value in med_update.dict().items():
        setattr(med, key, value)
    db.commit()
    db.refresh(med)
    return med

# Delete
@router.delete("/{medicine_id}")
def delete_medicine(medicine_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Delete a medicine from the current user's inventory.
    """
    med = db.query(models.Medicine).filter(models.Medicine.id == medicine_id, models.Medicine.user_id == current_user.id).first()
    if not med:
        raise HTTPException(status_code=404, detail="Medicine not found")
    db.delete(med)
    db.commit()
    return {"message": "Medicine deleted successfully"}
