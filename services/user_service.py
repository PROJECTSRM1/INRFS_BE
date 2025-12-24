from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.generated_models import UserRegistration
from schemas.user_schema import UserCreate
from utils.hash_password import hash_password, verify_password
from utils.otp_store import is_verified

from utils.jwt import create_access_token, create_refresh_token


def register_user(db: Session, data: UserCreate):
    # Check email exists
    if db.query(UserRegistration).filter(UserRegistration.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Check mobile exists
    if db.query(UserRegistration).filter(UserRegistration.mobile == data.mobile).first():
        raise HTTPException(status_code=400, detail="Mobile already registered")

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
        inv_reg_id=data.inv_reg_id,
        role_id=data.role_id,
        created_by=1,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "User registered successfully", "user_id": user.id}


# =====================================================
# LOGIN WITH OTP VERIFICATION CHECK
# =====================================================

def login_user(db: Session, data):

    # ❌ Neither provided
    if not data.email and not data.inv_reg_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or inv_reg_id is required",
        )

    # ❌ Both provided
    if data.email and data.inv_reg_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide only one: email or inv_reg_id",
        )

    # ✅ Determine identifier & fetch user
    if data.email:
        identifier = data.email
        user = (
            db.query(UserRegistration)
            .filter(UserRegistration.email == data.email)
            .first()
        )
    else:
        identifier = data.inv_reg_id
        user = (
            db.query(UserRegistration)
            .filter(UserRegistration.inv_reg_id == data.inv_reg_id)
            .first()
        )

    # ❌ User not found
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # ❌ OTP NOT VERIFIED → BLOCK LOGIN
    if not is_verified(identifier):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="OTP verification required before login",
        )

    # ❌ Password mismatch
    if not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # ===============================
    # ✅ GENERATE JWT TOKENS (HERE)
    # ===============================

    access_token = create_access_token(
        {
            "sub": user.inv_reg_id,     # subject
            "role_id": user.role_id,    # role for RBAC
        }
    )

    refresh_token = create_refresh_token(
        {
            "sub": user.inv_reg_id
        }
    )

    # ✅ FINAL RESPONSE
    return {
        "message": "Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }












# def login_user(db: Session, data):

#     # ❌ Neither provided
#     if not data.email and not data.inv_reg_id:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Email or inv_reg_id is required",
#         )

#     # ❌ Both provided
#     if data.email and data.inv_reg_id:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Provide only one: email or inv_reg_id",
#         )

#     # ✅ Determine identifier & fetch user
#     if data.email:
#         identifier = data.email
#         user = (
#             db.query(UserRegistration)
#             .filter(UserRegistration.email == data.email)
#             .first()
#         )
#     else:
#         identifier = data.inv_reg_id
#         user = (
#             db.query(UserRegistration)
#             .filter(UserRegistration.inv_reg_id == data.inv_reg_id)
#             .first()
#         )

#     # ❌ User not found
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid credentials",
#         )

#     # ❌ OTP NOT VERIFIED → BLOCK LOGIN
#     if not is_verified(identifier):
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="OTP verification required before login",
#         )

#     # ❌ Password mismatch
#     if not verify_password(data.password, user.password):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid credentials",
#         )

#     # ✅ SUCCESS (JWT generation comes next)
#     return {
#         "message": "Login successful",
#         "user_id": user.id,
#         "inv_reg_id": user.inv_reg_id,
#     }







# from sqlalchemy.orm import Session
# from fastapi import HTTPException, status


# from models.generated_models import UserRegistration
# from schemas.user_schema import UserCreate
# from utils.hash_password import hash_password, verify_password

# from utils.otp_store import is_verified

# def register_user(db: Session, data: UserCreate):
#     # Check email exists
#     if db.query(UserRegistration).filter(UserRegistration.email == data.email).first():
#         raise HTTPException(status_code=400, detail="Email already registered")

#     # Check mobile exists
#     if db.query(UserRegistration).filter(UserRegistration.mobile == data.mobile).first():
#         raise HTTPException(status_code=400, detail="Mobile already registered")

#     # Hash password
#     hashed_pwd = hash_password(data.password)

#     # Create user
#     user = UserRegistration(
#         first_name=data.first_name,
#         last_name=data.last_name,
#         email=data.email,
#         mobile=data.mobile,
#         password=hashed_pwd,
#         gender_id=data.gender_id,
#         age=data.age,
#         dob=data.dob,
#         inv_reg_id=data.inv_reg_id,
#         role_id=data.role_id,
#         created_by=1
#     )

#     db.add(user)
#     db.commit()
#     db.refresh(user)

#     return {"message": "User registered successfully", "user_id": user.id}






# def login_user(db: Session, data):
#     # ❌ Neither provided
#     if not data.email and not data.inv_reg_id:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Email or inv_reg_id is required",
#         )

#     # ❌ Both provided
#     if data.email and data.inv_reg_id:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Provide only one: email or inv_reg_id",
#         )

#     # ✅ Query by email OR inv_reg_id
#     if data.email:
#         user = (
#             db.query(UserRegistration)
#             .filter(UserRegistration.email == data.email)
#             .first()
#         )
#     else:
#         user = (
#             db.query(UserRegistration)
#             .filter(UserRegistration.inv_reg_id == data.inv_reg_id)
#             .first()
#         )

#     # ❌ User not found
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid credentials",
#         )

#     # ❌ Password mismatch (hashed)
#     if not verify_password(data.password, user.password):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid credentials",
#         )

#     # ✅ Success
#     return {
#         "message": "Login successful",
#         "user_id": user.id,
#         "inv_reg_id": user.inv_reg_id,
#     }

