from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine
from app.models import Base
from app.routers import auth, users, hospitals


app = FastAPI(title="FastAPI Auth Starter")

Base.metadata.create_all(bind=engine)


# CORS (adjust as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routers
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(hospitals.router)


@app.get("/")
def root():
    return {"message": "Hello World"}

