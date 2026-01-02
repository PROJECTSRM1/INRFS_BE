from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.generated_models import UserRegistration
from schemas.user_schema import UserCreate
from utils.hash_password import hash_password, verify_password
from utils.jwt import create_access_token, create_refresh_token
from services.otp_service import send_otp_service


# -----------------------------
# Generate inv_reg_id
# -----------------------------
def generate_inv_reg_id(db: Session):
    last_user = (
        db.query(UserRegistration)
        .order_by(UserRegistration.id.desc())
        .first()
    )

    if not last_user or not last_user.inv_reg_id:
        return "I0001"

    last_id = last_user.inv_reg_id  # e.g. I0005

    if not last_id.startswith("I") or not last_id[1:].isdigit():
        return "I0001"

    number = int(last_id[1:])
    return f"I{number + 1:04d}"


# -----------------------------
# REGISTER USER (AUTO OTP)
# -----------------------------
def register_user(db: Session, data: UserCreate):

    # 🔒 Allow ONLY normal users here
    if data.role_id != 1:
        raise HTTPException(
            status_code=403,
            detail="Only normal users can register here"
        )

    # Email already exists
    if db.query(UserRegistration).filter(
        UserRegistration.email == data.email
    ).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Mobile already exists
    if db.query(UserRegistration).filter(
        UserRegistration.mobile == data.mobile
    ).first():
        raise HTTPException(status_code=400, detail="Mobile already registered")

    hashed_pwd = hash_password(data.password)
    new_inv_reg_id = generate_inv_reg_id(db)

    user = UserRegistration(
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        mobile=data.mobile,
        password=hashed_pwd,
        gender_id=data.gender_id,
        age=data.age,
        dob=data.dob,
        inv_reg_id=new_inv_reg_id,
        role_id=data.role_id,   # ✅ comes from request
        created_by=1,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # ✅ Auto send OTP
    send_otp_service(db, user.email)

    return {
        "message": "User registered successfully. OTP sent to email.",
        "user_id": user.id,
        "inv_reg_id": user.inv_reg_id,
    }


# -----------------------------
# LOGIN USER (OTP PROTECTED)
# -----------------------------
def login_user(db: Session, data):

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

    if data.email:
        user = db.query(UserRegistration).filter(
            UserRegistration.email == data.email
        ).first()
    else:
        user = db.query(UserRegistration).filter(
            UserRegistration.inv_reg_id == data.inv_reg_id
        ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="OTP verification required before login",
        )

    if not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )



    access_token = create_access_token({
    "sub": user.inv_reg_id,   # 🔑 PRIMARY IDENTITY
    "user_id": user.id,       # optional (DB joins)
    "role_id": user.role_id
})

    refresh_token = create_refresh_token({
    "sub": user.inv_reg_id,
    "user_id": user.id,
    "role_id": user.role_id
})



    # access_token = create_access_token(
    #     {"user_id": user.id,            # ✅ BIGINT (for DB relations)
    #     "inv_reg_id": user.inv_reg_id, # ✅ Customer visible ID
    #     "role_id": user.role_id
    #     }
    # )
    # refresh_token = create_refresh_token(
    #     {"inv_reg_id": user.inv_reg_id,
    #     "role_id": user.role_id
    #     }
    # )

    return {
        "message": "Login successful",
        "Customer-ID": user.inv_reg_id,
        "First_Name": user.first_name,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


# -----------------------------
# CRUD OPERATIONS
# -----------------------------
def get_all_users(db: Session):
    return db.query(UserRegistration).all()


def get_user_by_id(db: Session, user_id: int):
    return db.query(UserRegistration).filter(
        UserRegistration.id == user_id
    ).first()


def update_user(db: Session, user_id: int, data):
    user = get_user_by_id(db, user_id)
    if not user:
        return None

    for field, value in data.dict(exclude_unset=True).items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int):
    user = get_user_by_id(db, user_id)
    if not user:
        return None

    db.delete(user)
    db.commit()
    return True
