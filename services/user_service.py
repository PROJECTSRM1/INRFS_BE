from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from sqlalchemy import func

from models.generated_models import UserRegistration, InvConfig
from schemas.user_schema import UserCreate
from utils.hash_password import hash_password, verify_password
from utils.jwt import create_access_token, create_refresh_token
from services.otp_service import send_otp_service
from utils.otp_store import store_user_data, is_user_registered


# --------------------------------------------------
# Generate Investor Registration ID
# --------------------------------------------------
def generate_inv_reg_id(db: Session):
    last_user = (
        db.query(UserRegistration)
        .filter(UserRegistration.inv_reg_id.isnot(None))
        .order_by(UserRegistration.id.desc())
        .first()
    )

    if not last_user:
        return "I0001"

    last_id = last_user.inv_reg_id
    if not last_id.startswith("I") or not last_id[1:].isdigit():
        return "I0001"

    return f"I{int(last_id[1:]) + 1:04d}"


# --------------------------------------------------
# REGISTER USER (ROLE-BASED)
# --------------------------------------------------
def register_user(db: Session, data: UserCreate):
    """
    role_id = 1 → Investor → OTP required
    role_id = 2 → Super Admin → Direct save
    role_id = 3 → Admin → Direct save
    """

    if data.role_id not in (1, 2, 3):
        raise HTTPException(status_code=400, detail="Invalid role_id")

    # -------------------------------
    # Duplicate checks
    # -------------------------------
    if db.query(UserRegistration).filter(
        UserRegistration.email == data.email
    ).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    if db.query(UserRegistration).filter(
        UserRegistration.mobile == data.mobile
    ).first():
        raise HTTPException(status_code=400, detail="Mobile already registered")

    # --------------------------------------------------
    # ✅ INVESTOR (OTP FLOW)
    # --------------------------------------------------
    if data.role_id == 1:
        # Store user data temporarily (memory)
        store_user_data(data.email, data.model_dump())

        # Send OTP
        send_otp_service(db, data.email)



        return {
            "message": "OTP sent successfully. Verify OTP to complete registration"
        }

    # --------------------------------------------------
    # ✅ ADMIN / SUPER ADMIN (DIRECT SAVE)
    # --------------------------------------------------
    hashed_pwd = hash_password(data.password)

    user = UserRegistration(
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        mobile=data.mobile,
        password=hashed_pwd,
        gender_id=data.gender_id,
        age=data.age,
        dob=data.dob,
        inv_reg_id=None,       # Admins don’t need Investor ID
        role_id=data.role_id,
        is_verified=True,      # No OTP required
        created_by=1,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message": "User registered successfully",
        "user_id": user.id,
        "role_id": user.role_id,
    }


# --------------------------------------------------
# LOGIN USER (UPDATED – with is_active check)
# --------------------------------------------------
def login_user(db: Session, data):

    # -------------------------
    # INPUT VALIDATION
    # -------------------------
    if not data.email and not data.inv_reg_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or inv_reg_id is required",
        )

    if data.email and data.inv_reg_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide only one: email or inv_reg_id",
        )

    # -------------------------
    # FETCH USER
    # -------------------------
    if data.inv_reg_id:
        user = db.query(UserRegistration).filter(
            UserRegistration.inv_reg_id == data.inv_reg_id
        ).first()
    else:
        user = db.query(UserRegistration).filter(
            UserRegistration.email == data.email
        ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # -------------------------
    # ACCOUNT ACTIVE CHECK (NEW)
    # -------------------------
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive. Please contact support."
        )

    # -------------------------
    # OTP CHECK (INVESTORS ONLY)
    # -------------------------
    if user.role_id == 1 and not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="OTP verification required before login",
        )

    # -------------------------
    # PASSWORD CHECK
    # -------------------------
    if not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # -------------------------
    # TOKEN GENERATION
    # -------------------------
    subject = user.inv_reg_id if user.inv_reg_id else str(user.id)

    access_token = create_access_token({
        "sub": subject,
        "user_id": user.id,
        "role_id": user.role_id
    })

    refresh_token = create_refresh_token({
        "sub": subject,
        "user_id": user.id,
        "role_id": user.role_id
    })

    return {
        "message": "Login successful",
        "Customer-ID": user.inv_reg_id,
        "First_Name": user.first_name,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }
def resend_otp_service(db: Session, email: str):
    """
    Resend OTP for a user who has a pending registration.
    """

    # -------------------------
    # Check if user has pending registration
    # -------------------------
    if not is_user_registered(email):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No pending registration found for this email."
        )

    # -------------------------
    # Optional: Rate limit check
    # -------------------------
    # You can implement a simple counter in memory or a database table
    # to prevent abuse. Example:
    # if too_many_attempts(email):
    #     raise HTTPException(status_code=429, detail="Too many OTP requests. Try later.")

    # -------------------------
    # Resend OTP
    # -------------------------
    send_otp_service(db, email)

    return {"message": "OTP resent successfully. Please check your email."}








# def login_user(db: Session, data):

#     if not data.email and not data.inv_reg_id:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Email or inv_reg_id is required",
#         )

#     if data.email and data.inv_reg_id:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Provide only one: email or inv_reg_id",
#         )

#     if data.inv_reg_id:
#         user = db.query(UserRegistration).filter(
#             UserRegistration.inv_reg_id == data.inv_reg_id
#         ).first()
#     else:
#         user = db.query(UserRegistration).filter(
#             UserRegistration.email == data.email
#         ).first()

#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid credentials",
#         )

#     if user.role_id == 1 and not user.is_verified:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="OTP verification required before login",
#         )

#     if not verify_password(data.password, user.password):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid credentials",
#         )

#     subject = user.inv_reg_id if user.inv_reg_id else str(user.id)

#     access_token = create_access_token({
#         "sub": subject,
#         "user_id": user.id,
#         "role_id": user.role_id
#     })

#     refresh_token = create_refresh_token({
#         "sub": subject,
#         "user_id": user.id,
#         "role_id": user.role_id
#     })

#     return {
#         "message": "Login successful",
#         "Customer-ID": user.inv_reg_id,
#         "First_Name": user.first_name,
#         "access_token": access_token,
#         "refresh_token": refresh_token,
#         "token_type": "bearer",
#     }


# --------------------------------------------------
# CRUD OPERATIONS (UNCHANGED)
# --------------------------------------------------
def get_all_users(db: Session):
    users = db.query(UserRegistration).all()
    response = []

    for user in users:
        user_data = {
            "id": user.id,
            "inv_reg_id": user.inv_reg_id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "mobile": user.mobile,
            "role_id": user.role_id,
            "gender_id": user.gender_id,
            "age": user.age,
            "dob": user.dob,
        }

        if user.role_id == 1:
            agg = (
                db.query(
                    func.coalesce(func.sum(InvConfig.principal_amount), 0),
                    func.coalesce(func.sum(InvConfig.maturity_amount), 0),
                    func.min(InvConfig.created_date),
                    func.max(InvConfig.maturity_date),
                )
                .filter(InvConfig.created_by == user.id)
                .first()
            )

            user_data.update({
                "total_principal_amount": agg[0],
                "total_maturity_amount": agg[1],
                "investment_created_date": agg[2],
                "investment_maturity_date": agg[3],
            })

        response.append(user_data)

    return response


def get_user_by_inv_reg_id(db: Session, inv_reg_id: str):
    return (
        db.query(UserRegistration)
        .filter(UserRegistration.inv_reg_id == inv_reg_id)
        .first()
    )


def update_user(db: Session, inv_reg_id: str, data):
    user = get_user_by_inv_reg_id(db, inv_reg_id)
    if not user:
        return None

    for field, value in data.dict(exclude_unset=True).items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user



def delete_user(db: Session, inv_reg_id: str):
    user = get_user_by_inv_reg_id(db, inv_reg_id)
    if not user:
        return None

    has_investments = (
        db.query(InvConfig)
        .filter(InvConfig.created_by == user.id)
        .first()
    )

    if has_investments:
        raise HTTPException(
            status_code=400,
            detail="User cannot be deleted because investments exist"
        )

    db.delete(user)
    db.commit()
    return True



