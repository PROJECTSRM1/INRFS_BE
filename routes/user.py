from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db

from schemas.user_schema import (
    UserCreate,
    UserLogin,
    SendOTPRequest,
    VerifyOTPRequest,
    UserUpdate,
    UserDetailResponse,
)

from services.user_service import (
    register_user,
    login_user,
    get_all_users,
    get_user_by_id,
    update_user,
    delete_user,
)

from services.otp_service import (
    send_otp_service,
    verify_otp_service,
)

from jose import jwt, JWTError
from utils.jwt import create_access_token, SECRET_KEY, ALGORITHM




router = APIRouter(prefix="/users", tags=["Users"])




@router.post("/register")
#@router.post("/register", response_model=UserResponse)
def register(data: UserCreate, db: Session = Depends(get_db)):
    return register_user(db, data)



@router.post("/send-otp")
def send_otp(data: SendOTPRequest, db: Session = Depends(get_db)):
    return send_otp_service(db, data.email)



@router.post("/verify-otp")
def verify_otp(data: VerifyOTPRequest):
    return verify_otp_service(data.email, data.otp)



@router.post("/login")
def login(data: UserLogin, db: Session = Depends(get_db)):
    return login_user(db, data)




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
    


   
@router.get("/", response_model=List[UserDetailResponse])
def list_users(db: Session = Depends(get_db)):
    return get_all_users(db)



@router.get("/{user_id}", response_model=UserDetailResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user



@router.put("/{user_id}", response_model=UserDetailResponse)
def update_user_api(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
):
    user = update_user(db, user_id, data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}")
def delete_user_api(user_id: int, db: Session = Depends(get_db)):
    deleted = delete_user(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}






































# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session

# from core.database import get_db
# <<<<<<< HEAD
# =======
# from models.generated_models import UserRegistration
# >>>>>>> main

# from models.generated_models import UserRegistration
# from services.user_service import register_user, login_user

# <<<<<<< HEAD
# from jose import jwt, JWTError
# from utils.jwt import create_access_token, SECRET_KEY, ALGORITHM

# =======
# >>>>>>> main
# from schemas.user_schema import (
#     UserCreate,
#     UserLogin,
#     SendOTPRequest,
#     VerifyOTPRequest,
#     UserResponse,     # ✅ Added import
# )

# from services.otp_service import (
#     send_otp_service,
#     verify_otp_service,
# )

# router = APIRouter(prefix="/users", tags=["Users"])


# <<<<<<< HEAD
# # =========================
# # REGISTER
# # =========================
# @router.post("/register")
# =======
# @router.post("/register", response_model=UserResponse)
# >>>>>>> main
# def register(data: UserCreate, db: Session = Depends(get_db)):
#     return register_user(db, data)


# # =========================
# # LOGIN
# # =========================
# @router.post("/login")
# def login(data: UserLogin, db: Session = Depends(get_db)):
#     return login_user(db, data)


# <<<<<<< HEAD
# # =========================
# # REFRESH TOKEN  ✅ ADD HERE
# # =========================
# @router.post("/refresh-token")
# def refresh_token(token: str):
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

#         # Ensure this is a refresh token
#         if payload.get("type") != "refresh":
#             raise HTTPException(status_code=401, detail="Invalid token")

#         access_token = create_access_token(
#             {"sub": payload["sub"]}
#         )

#         return {
#             "access_token": access_token,
#             "token_type": "bearer"
#         }

#     except JWTError:
#         raise HTTPException(status_code=401, detail="Invalid refresh token")


# # =========================
# # SEND OTP
# # =========================
# =======
# >>>>>>> main
# @router.post("/send-otp")
# def send_otp(data: SendOTPRequest, db: Session = Depends(get_db)):
#     return send_otp_service(db, data.email)


# # =========================
# # VERIFY OTP
# # =========================
# @router.post("/verify-otp")
# def verify_otp(data: VerifyOTPRequest):
#     return verify_otp_service(data.email, data.otp)
