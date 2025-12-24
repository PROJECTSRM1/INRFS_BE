from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_db
# from models.user import User
from models.generated_models import UserRegistration

from services.user_service import register_user, login_user

#from schemas.user_schema import UserCreate, UserLogin

from schemas.user_schema import (
    UserCreate,
    UserLogin,
    SendOTPRequest,
    VerifyOTPRequest,
)

from services.otp_service import (
    send_otp_service,
    verify_otp_service,
)




router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register")
def register(data: UserCreate, db: Session = Depends(get_db)):
    return register_user(db, data)


@router.post("/login")
def login(data: UserLogin, db: Session = Depends(get_db)):
    return login_user(db, data)





@router.post("/send-otp")
def send_otp(data: SendOTPRequest, db: Session = Depends(get_db)):
    return send_otp_service(db, data.email)


@router.post("/verify-otp")
def verify_otp(data: VerifyOTPRequest):
    return verify_otp_service(data.email, data.otp)
