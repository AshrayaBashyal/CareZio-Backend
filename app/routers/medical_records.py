from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models, schemas
from app.oauth2 import get_current_user
from app.cloudinary import upload_medical_file, delete_medical_file

router = APIRouter(
    prefix="/medical-records",
    tags=["Medical Records"],
)


@router.post(
    "/",
    response_model=schemas.MedicalRecordOut,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a medical record",
    description="Upload a medical document such as prescriptions, reports, X-rays, or PDFs. Files are securely stored and linked to your account.",
)
async def upload_medical_record(
    title: str = Form(..., description="Short title for this medical record (e.g. 'Blood Test Report')"),
    file: UploadFile = File(..., description="Medical file (PDF, JPG, or PNG)"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Upload a new medical record.

    Supported formats:
    - PDF
    - JPG
    - PNG

    The file is uploaded to secure cloud storage and linked to the logged-in user.
    """

    if not file.content_type:
        raise HTTPException(status_code=400, detail="Invalid file")

    allowed_types = ["image/jpeg", "image/png", "application/pdf"]

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, PNG, and PDF files are allowed",
        )

    try:
        file_url, file_type = upload_medical_file(file.file)
    except Exception:
        raise HTTPException(status_code=500, detail="File upload failed")

    record = models.MedicalRecord(
        user_id=current_user.id,
        title=title,
        file_url=file_url,
        file_type=file_type,
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record


@router.get(
    "/",
    response_model=List[schemas.MedicalRecordOut],
    summary="Get medical records",
    description="Retrieve all medical documents uploaded by the current user.",
)
def get_medical_records(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Returns all medical records uploaded by the authenticated user,
    ordered from newest to oldest.
    """
    return (
        db.query(models.MedicalRecord)
        .filter(models.MedicalRecord.user_id == current_user.id)
        .order_by(models.MedicalRecord.uploaded_at.desc())
        .all()
    )


@router.delete(
    "/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a medical record",
    description="Delete a medical record by its ID. Also removes the file from Cloudinary."
)
def delete_medical_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    record = db.query(models.MedicalRecord).filter(
        models.MedicalRecord.id == record_id,
        models.MedicalRecord.user_id == current_user.id
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    # delete from Cloudinary
    delete_medical_file(record.file_url)

    # delete from DB
    db.delete(record)
    db.commit()
    return {"detail": "Record deleted successfully"}
