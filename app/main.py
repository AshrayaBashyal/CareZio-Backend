from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
from contextlib import asynccontextmanager

from app.database import engine
from app.models import Base
from app.routers import auth, users, hospitals, medicines, intakes, schedules, notifications
from app.scheduler import start_scheduler

# create tables (dev only). In production use alembic
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager for application startup/shutdown events.
    """
    start_scheduler()
    print("[App] Scheduler started")
    yield
    print("[App] App shutting down")

app = FastAPI(
    title="CareZio API",
    description="API for digital medical assistant with medication management system with reminders and inventory tracking",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include routers
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(hospitals.router)
app.include_router(medicines.router)
app.include_router(intakes.router)
app.include_router(schedules.router)
app.include_router(notifications.router)

@app.get("/")
def root():
    """
    Root endpoint to verify the API is running.
    """
    return {"message": "CareZio API is running"}

@app.get("/health")
def health_check():
    """
    Health check endpoint: returns status, timestamp, and version.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0"
    }

@app.get("/info")
def api_info():
    """
    Endpoint providing API name, version, description, and features.
    """
    return {
        "name": "CareZio API",
        "version": "1.0.0",
        "description": "Comprehensive digital medical assistant with medication management system with reminders and inventory tracking",
        "features": [
            "User authentication and management",
            "Medicine inventory tracking",
            "Flexible scheduling with multiple daily times",
            "Push notifications for reminders",
            "Low inventory alerts",
            "Hospital search functionality"
        ]
    }
