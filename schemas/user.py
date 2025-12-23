from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    mobile: str = Field(..., min_length=10, max_length=10)
    password: str = Field(..., min_length=6)

class UserUpdate(BaseModel):
    full_name: str | None = None
    mobile: str | None = None

class UserResponse(BaseModel):
    id: int
    customer_id: str 
    full_name: str
    email: EmailStr
    mobile: str
    is_email_verified: bool
    is_mobile_verified: bool

    class Config:
        from_attributes = True
