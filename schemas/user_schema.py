from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    mobile: str
    password: str
    gender_id: int
    age: int
    dob: date
    inv_reg_id: str
    role_id: int


class UserLogin(BaseModel):
    email: Optional[EmailStr] = None
    inv_reg_id: Optional[str] = None
    password: str


class SendOTPRequest(BaseModel):
    email: str


class VerifyOTPRequest(BaseModel):
    email: str
    otp: str
