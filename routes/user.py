from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db

from schemas.user_schema import (
    UserCreate,
    UserLogin,
    VerifyOTPRequest,
    UserUpdate,
    UserDetailResponse,
    LoginResponse,   # ✅ ADD THIS
    UserDetailBasicResponse
)


from services.user_service import (
    register_user,
    login_user,
    get_all_users,
    get_user_by_inv_reg_id,
    update_user,
    delete_user,
)


from services.otp_service import verify_otp_service

from jose import jwt, JWTError
from utils.jwt import create_access_token, SECRET_KEY, ALGORITHM



from schemas.bank_schema import (
    BankDetailsCreate,
    BankDetailsResponse,
)
from services.bank_service import (
    add_or_update_bank_details,
    get_bank_details,
    get_all_bank_details,

)


from utils.auth import get_current_user

from models.generated_models import UserRegistration


from schemas.user_schema import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
)

from services.password_service import (
    forgot_password_service,
    reset_password_service,
)



router = APIRouter(prefix="/users", tags=["Users"])


# =========================
# REGISTER (AUTO OTP)
# =========================
@router.post("/register")
def register(data: UserCreate, db: Session = Depends(get_db)):
    return register_user(db, data)


# =========================
# VERIFY OTP
# =========================
@router.post("/verify-otp")
def verify_otp(data: VerifyOTPRequest, db: Session = Depends(get_db)):
    return verify_otp_service(db, data.email, data.otp)


# =========================
# LOGIN
# =========================
@router.post("/login", response_model=LoginResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    return login_user(db, data)


# -------------------------
# FORGOT PASSWORD
# -------------------------
@router.post("/forgot-password")
def forgot_password(
    data: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    return forgot_password_service(db, data.email)


# -------------------------
# RESET PASSWORD
# -------------------------
@router.post("/reset-password")
def reset_password(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    return reset_password_service(
        db,
        token=data.token,
        new_password=data.new_password,
    )



# =========================
# REFRESH TOKEN
# =========================
@router.post("/refresh-token")
def refresh_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token")

        access_token = create_access_token(
            {"sub": payload["sub"], "role_id": payload.get("role_id")}
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
        }

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")






# -----------------------------
# ADD / UPDATE BANK DETAILS
# -----------------------------
@router.post("/bank-details")
def add_bank_details(
    data: BankDetailsCreate,
    db: Session = Depends(get_db),
    current_user: UserRegistration = Depends(get_current_user),
):
    return add_or_update_bank_details(
        db=db,
        user_id=current_user.id,
        bank_id=data.bank_id,
        bank_account_no=data.bank_account_no,
        ifsc_code=data.ifsc_code,
    )


# -----------------------------
# GET BANK DETAILS
# -----------------------------

@router.get("/bank-details")
def fetch_bank_details(
    db: Session = Depends(get_db),
    current_user: UserRegistration = Depends(get_current_user),
):
    # Admin / SuperAdmin
    if current_user.role_id in (2, 3):
        return get_all_bank_details(db)

    # Investor
    return get_bank_details(db, current_user.id)




# @router.get("/bank-details", response_model=BankDetailsResponse)
# def fetch_bank_details(db: Session = Depends(get_db), current_user: UserRegistration = Depends(get_current_user)):
#     return get_bank_details(db, current_user.id)

# from utils.auth import admin_or_superadmin


# @router.get("/bank-details")
# def fetch_bank_details(
#     db: Session = Depends(get_db),
#     current_user: UserRegistration = Depends(admin_or_superadmin),
# ):
#     return get_bank_details(db)





# =========================
# CRUD OPERATIONS
# =========================
@router.get("/", response_model=List[UserDetailResponse])
def list_users(db: Session = Depends(get_db)):
    return get_all_users(db)



@router.get("/{inv_reg_id}", response_model=UserDetailBasicResponse)
def get_user(inv_reg_id: str, db: Session = Depends(get_db)):
    user = get_user_by_inv_reg_id(db, inv_reg_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{inv_reg_id}", response_model=UserDetailBasicResponse)
def update_user_api(
    inv_reg_id: str,
    data: UserUpdate,
    db: Session = Depends(get_db),
):
    user = update_user(db, inv_reg_id, data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user



@router.delete("/{inv_reg_id}")
def delete_user_api(inv_reg_id: str, db: Session = Depends(get_db)):
    deleted = delete_user(db, inv_reg_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}










