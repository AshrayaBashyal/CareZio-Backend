from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

"""
Database connection and session setup using SQLAlchemy.
"""

SQLALCHEMY_DATABASE_URL = settings.assembled_db_url

# Use pool_pre_ping to avoid stale connections (good for cloud DBs)
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """
    Dependency to get a new database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
