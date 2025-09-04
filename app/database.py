from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings


SQLALCHEMY_DATABASE_URL = (
f"postgresql://{settings.database_username}:"
f"{settings.database_password}@{settings.database_hostname}:"
f"{settings.database_port}/{settings.database_name}"
)


engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


# Dependency for routes
from typing import Generator


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()