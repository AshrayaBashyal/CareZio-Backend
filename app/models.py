from sqlalchemy import (
    Column, Integer, String, Boolean, TIMESTAMP, text,
    ForeignKey, DateTime, Time, func
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class User(Base):
    """User model: accounts with credentials."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, server_default=text("true"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    medicines = relationship("Medicine", back_populates="user", cascade="all, delete-orphan")
    intakes = relationship("MedicineIntakeLog", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    fcm_tokens = relationship("UserFCMToken", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User id={self.id} email={self.email}>"


class UserFCMToken(Base):
    """Stores FCM tokens linked to users. Supports multiple tokens per user."""
    __tablename__ = "user_fcm_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    fcm_token = Column(String, index=True)  # not unique → same token can belong to multiple users
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="fcm_tokens")

    def __repr__(self):
        return f"<UserFCMToken id={self.id} user_id={self.user_id}>"


class Medicine(Base):
    __tablename__ = "medicines"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name = Column(String, nullable=False)
    dosage = Column(String, nullable=True)
    inventory = Column(Integer, default=0)
    low_threshold = Column(Integer, default=5, nullable=False)

    user = relationship("User", back_populates="medicines")
    schedules = relationship("MedicineSchedule", back_populates="medicine", cascade="all, delete-orphan")
    intakes = relationship("MedicineIntakeLog", back_populates="medicine", cascade="all, delete-orphan")
    def __repr__(self):
        return f"<Medicine id={self.id} name={self.name} inventory={self.inventory} low_threshold={self.low_threshold}>"


class MedicineSchedule(Base):
    __tablename__ = "medicine_schedules"

    id = Column(Integer, primary_key=True, index=True)
    medicine_id = Column(Integer, ForeignKey("medicines.id", ondelete="CASCADE"), index=True)
    frequency_type = Column(String, nullable=False)  # daily / every_n_days
    frequency_value = Column(Integer, nullable=True)  # e.g. 2 → every 2 days
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    medicine = relationship("Medicine", back_populates="schedules")
    times = relationship("ScheduleTime", back_populates="schedule", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<MedicineSchedule id={self.id} medicine_id={self.medicine_id}>"


class ScheduleTime(Base):
    __tablename__ = "schedule_times"

    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("medicine_schedules.id", ondelete="CASCADE"), index=True)
    time_of_day = Column(Time, nullable=False)  # e.g., 08:00, 14:00, 20:00

    schedule = relationship("MedicineSchedule", back_populates="times")

    def __repr__(self):
        return f"<ScheduleTime id={self.id} time={self.time_of_day}>"


class MedicineIntakeLog(Base):
    __tablename__ = "medicine_intake_logs"

    id = Column(Integer, primary_key=True, index=True)
    medicine_id = Column(Integer, ForeignKey("medicines.id", ondelete="CASCADE"), index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    taken_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="intakes")
    medicine = relationship("Medicine", back_populates="intakes")

    def __repr__(self):
        return f"<MedicineIntakeLog id={self.id} medicine_id={self.medicine_id}>"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    notification_type = Column(String, nullable=False)  # 'reminder', 'inventory', 'system'
    is_read = Column(Boolean, default=False)
    related_entity_type = Column(String, nullable=True)  # 'medicine', 'schedule', etc.
    related_entity_id = Column(Integer, nullable=True)  # ID of related entity
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="notifications")

    def __repr__(self):
        return f"<Notification id={self.id} type={self.notification_type}>"
