from pydantic import BaseModel, EmailStr, Field
from datetime import date
from typing import Optional



class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    mobile: str = Field(..., min_length=10, max_length=10)
    password: str = Field(..., min_length=6)
    gender_id: int
    age: int
    dob: date

    role_id: int = Field(..., description="1 = User, 2 = Admin")



class UserLogin(BaseModel):
    email: Optional[EmailStr] = None
    inv_reg_id: Optional[str] = None
    password: str


class LoginResponse(BaseModel):
    message: str
    inv_reg_id: str = Field(alias="Customer-ID")
    first_name: str = Field(alias="First_Name")
    access_token: str
    refresh_token: str
    token_type: str


class SendOTPRequest(BaseModel):
    email: str


class VerifyOTPRequest(BaseModel):
    email: str
    otp: str



class UserResponse(BaseModel):
    id: int
    inv_reg_id: str
    role_id: int

    class Config:
        from_attributes = True


      
class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    mobile: Optional[str] = Field(None, min_length=10, max_length=10)
    gender_id: Optional[int] = None
    age: Optional[int] = None
    dob: Optional[date] = None


class UserDetailResponse(BaseModel):
    id: int
    inv_reg_id: str
    first_name: str
    last_name: str
    email: EmailStr
    mobile: str
    role_id: int
    gender_id: int
    age: int
    dob: date

    class Config:
        from_attributes = True


