from pydantic import BaseModel, EmailStr, Field
from datetime import date
from typing import Optional


# ------------------------------
# User Registration Schema
# ------------------------------
class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    mobile: str = Field(..., min_length=10, max_length=10)
    password: str = Field(..., min_length=6)
    # gender_id: int
    # age: int
    # dob: date


# ------------------------------
# User Login Schema
# ------------------------------
class UserLogin(BaseModel):
    email: Optional[EmailStr] = None
    inv_reg_id: Optional[str] = None
    password: str


# ------------------------------
# OTP Schemas
# ------------------------------
class SendOTPRequest(BaseModel):
    email: str


class VerifyOTPRequest(BaseModel):
    email: str
    otp: str


# ------------------------------
# User Response Schema
# ------------------------------
class UserResponse(BaseModel):
    id: int
    inv_reg_id: str
    role_id: int

    class Config:
        from_attributes = True

