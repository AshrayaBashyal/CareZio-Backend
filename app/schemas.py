from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional, List


# ---------- Users ----------
class UserBase(BaseModel):
    full_name: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True


#------------- Hospitals ---------------
class Hospital(BaseModel):
    name: str
    address: str
    phone: List[str]
    ambulances: int
    doctors: List[str]
    nurses: List[str]
    ambulance_driver_phone: List[str]
    ambulance_driver_address: List[str]
    image_url: HttpUrl


# ---------- Auth / Token ----------
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[int] = None