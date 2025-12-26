from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db

from schemas.user_schema import (
    UserCreate,
    UserLogin,
    SendOTPRequest,
    VerifyOTPRequest,
    UserResponse,     # ✅ Added import
)

from services.user_service import register_user, login_user

from services.otp_service import (
    send_otp_service,
    verify_otp_service,
)

from jose import jwt, JWTError
from utils.jwt import create_access_token, SECRET_KEY, ALGORITHM

# from models.generated_models import UserRegistration


router = APIRouter(prefix="/users", tags=["Users"])



# =========================
# REGISTER
# =========================
@router.post("/register")
#@router.post("/register", response_model=UserResponse)
def register(data: UserCreate, db: Session = Depends(get_db)):
    return register_user(db, data)


# -----------------------------
# Send OTP (after registration)
# -----------------------------
@router.post("/send-otp")
def send_otp(data: SendOTPRequest, db: Session = Depends(get_db)):
    return send_otp_service(db, data.email)


# =========================
# VERIFY OTP
# =========================
# @router.post("/verify-otp")
# def verify_otp(data: VerifyOTPRequest):
#     return verify_otp_service(data.email, data.otp)

@router.post("/verify-otp")
def verify_otp(data: VerifyOTPRequest, db: Session = Depends(get_db)):
    return verify_otp_service(db, data.email, data.otp)


# -----------------------------
# Login (email OR inv_reg_id)
# -----------------------------
@router.post("/login")
def login(data: UserLogin, db: Session = Depends(get_db)):
    return login_user(db, data)



# =========================
# REFRESH TOKEN           
# =========================
@router.post("/refresh-token")
def refresh_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Ensure this is a refresh token
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token")

        access_token = create_access_token(
            {"sub": payload["sub"]}
        )

        # access_token = create_access_token(
        #     {"sub": payload["sub"], "role_id": payload.get("role_id")}
        # )


        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")



