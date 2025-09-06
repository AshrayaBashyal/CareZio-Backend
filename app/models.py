from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, text, ForeignKey, DateTime, Time
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    """
    User model: accounts with credentials and optional FCM token.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, server_default=text("true"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))

    fcm_token = Column(String, nullable=True)

    medicines = relationship("Medicine", back_populates="user", cascade="all, delete-orphan")
    intakes = relationship("MedicineIntakeLog", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")

class Medicine(Base):
    """
    Medicine model representing a medicine in user's inventory.
    """
    __tablename__ = "medicines"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    name = Column(String, nullable=False)
    dosage = Column(String, nullable=True)
    inventory = Column(Integer, default=0)
    low_threshold = Column(Integer, nullable=True)  # optional threshold for low inventory alerts

    user = relationship("User", back_populates="medicines")
    schedules = relationship("MedicineSchedule", back_populates="medicine", cascade="all, delete-orphan")
    intakes = relationship("MedicineIntakeLog", back_populates="medicine", cascade="all, delete-orphan")

class MedicineSchedule(Base):
    """
    Schedule for a medicine:
    - frequency_type: 'daily' or 'every_n_days'
    - frequency_value: interval if using 'every_n_days'
    """
    __tablename__ = "medicine_schedules"

    id = Column(Integer, primary_key=True, index=True)
    medicine_id = Column(Integer, ForeignKey("medicines.id", ondelete="CASCADE"))
    frequency_type = Column(String, nullable=False)  # daily / every_n_days
    frequency_value = Column(Integer, nullable=True)  # e.g., 2 (every 2 days)
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))

    medicine = relationship("Medicine", back_populates="schedules")
    times = relationship("ScheduleTime", back_populates="schedule", cascade="all, delete-orphan")

class ScheduleTime(Base):
    """
    Time of day for a schedule (stored in UTC).
    """
    __tablename__ = "schedule_times"

    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("medicine_schedules.id", ondelete="CASCADE"))
    time_of_day = Column(Time, nullable=False)  # e.g., 08:00:00 (UTC)

    schedule = relationship("MedicineSchedule", back_populates="times")

class MedicineIntakeLog(Base):
    """
    Log entry for when a medicine was taken.
    """
    __tablename__ = "medicine_intake_logs"

    id = Column(Integer, primary_key=True, index=True)
    medicine_id = Column(Integer, ForeignKey("medicines.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    taken_at = Column(DateTime(timezone=True), server_default=text("now()"))

    user = relationship("User", back_populates="intakes")
    medicine = relationship("Medicine", back_populates="intakes")

class Notification(Base):
    """
    Notification model for user alerts (types include 'reminder', 'inventory', 'system').
    """
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    notification_type = Column(String, nullable=False)  # 'reminder', 'inventory', 'system'
    is_read = Column(Boolean, default=False)
    related_entity_type = Column(String, nullable=True)  # e.g., 'medicine', 'schedule'
    related_entity_id = Column(Integer, nullable=True)   # ID of the related entity
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))

    user = relationship("User", back_populates="notifications")
