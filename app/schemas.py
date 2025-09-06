from pydantic import BaseModel, EmailStr, HttpUrl, Field
from typing import Optional, List
from datetime import datetime, time

"""
Pydantic schemas for request and response models.
"""

# ---------- Users ----------
class UserBase(BaseModel):
    full_name: Optional[str] = Field(None, description="Full name of the user")
    email: EmailStr = Field(..., description="User email address (unique)")

class UserCreate(UserBase):
    password: str = Field(..., description="User password")

class UserOut(UserBase):
    id: int = Field(..., description="User ID")
    is_active: bool = Field(..., description="Is the user account active?")

    class Config:
        from_attributes = True

# ---------- Hospitals (static) ----------
class Hospital(BaseModel):
    name: str = Field(..., description="Hospital name")
    address: str = Field(..., description="Hospital address")
    phone: List[str] = Field(..., description="Contact phone numbers (with country code)")
    ambulances: int = Field(..., description="Number of ambulances available")
    doctors: List[str] = Field(..., description="Names of doctors")
    nurses: List[str] = Field(..., description="Names of nurses")
    ambulance_driver_phone: List[str] = Field(..., description="Phone numbers of ambulance drivers")
    ambulance_driver_address: List[str] = Field(..., description="Addresses of ambulance drivers")
    image_url: HttpUrl = Field(..., description="URL of hospital image or logo")

# ---------- Auth / Token ----------
class Token(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(..., description="Token type (e.g. 'bearer')")

class TokenData(BaseModel):
    id: Optional[int] = Field(None, description="ID of the user from token")

# ---------- Medicine ----------
class MedicineBase(BaseModel):
    name: str = Field(..., description="Name of medicine")
    dosage: Optional[str] = Field(None, description="Dosage instructions")
    inventory: int = Field(..., description="Current inventory count (number of units left)")
    low_threshold: Optional[int] = Field(None, description="Threshold for low stock alerts")

class MedicineCreate(MedicineBase):
    pass

class MedicineOut(MedicineBase):
    id: int = Field(..., description="Medicine ID")

    class Config:
        from_attributes = True

# ---------- Schedule Time ----------
class ScheduleTimeBase(BaseModel):
    time_of_day: time = Field(..., description="Time of day in 24-hour format (HH:MM or HH:MM:SS)")

class ScheduleTimeOut(ScheduleTimeBase):
    id: int = Field(..., description="ID of the schedule time entry")

    class Config:
        form_attributes = True

class ScheduleTimeWithMedicineOut(ScheduleTimeOut):
    medicine_name: str = Field(..., description="Name of the associated medicine")
    medicine_dosage: Optional[str] = Field(None, description="Dosage of the associated medicine")

    class Config:
        from_attributes = True

# ---------- Medicine Schedule ----------
class MedicineScheduleBase(BaseModel):
    frequency_type: str = Field(..., description="Frequency type: 'daily' or 'every_n_days'")
    frequency_value: Optional[int] = Field(1, description="Interval (in days) when using 'every_n_days' frequency")

class MedicineScheduleCreate(MedicineScheduleBase):
    times: List[ScheduleTimeBase] = Field(..., description="List of times (in local timezone) for the schedule")

class MedicineScheduleUpdate(BaseModel):
    frequency_type: Optional[str] = Field(None, description="Frequency type to update ('daily' or 'every_n_days')")
    frequency_value: Optional[int] = Field(None, description="Interval (in days) to update for 'every_n_days'")
    times: Optional[List[ScheduleTimeBase]] = Field(None, description="Updated list of times in local timezone")

class MedicineScheduleOut(MedicineScheduleBase):
    id: int = Field(..., description="Schedule ID")
    times: List[ScheduleTimeOut]
    created_at: datetime = Field(..., description="Timestamp when schedule was created")

    class Config:
        from_attributes = True

class MedicineScheduleWithMedicineOut(MedicineScheduleOut):
    medicine: MedicineOut

    class Config:
        from_attributes = True

# ---------- Medicine Intake ----------
class MedicineIntakeCreate(BaseModel):
    medicine_id: int = Field(..., description="ID of the medicine to log intake for")

class MedicineIntakeOut(BaseModel):
    id: int = Field(..., description="Intake log ID")
    medicine_id: int = Field(..., description="ID of the medicine taken")
    taken_at: datetime = Field(..., description="Timestamp when medicine was taken (UTC)")

    class Config:
        from_attributes = True

class MedicineIntakeWithMedicineOut(MedicineIntakeOut):
    medicine_name: str = Field(..., description="Name of the medicine")
    medicine_dosage: Optional[str] = Field(None, description="Dosage of the medicine")

    class Config:
        from_attributes = True

# ---------- Notifications ----------
class NotificationBase(BaseModel):
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification message body")
    notification_type: str = Field(..., description="Type of notification (e.g. 'reminder', 'inventory', 'system')")
    related_entity_type: Optional[str] = Field(None, description="Type of related entity ('medicine', 'schedule', etc.)")
    related_entity_id: Optional[int] = Field(None, description="ID of the related entity")

class NotificationCreate(NotificationBase):
    pass

class NotificationOut(NotificationBase):
    id: int = Field(..., description="Notification ID")
    is_read: bool = Field(..., description="Read status of the notification")
    created_at: datetime = Field(..., description="Timestamp when notification was created")
    user_id: int = Field(..., description="ID of the user this notification belongs to")

    class Config:
        from_attributes = True

class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = Field(None, description="Set to true to mark notification as read, false for unread")
