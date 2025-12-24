from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.generated_models import UserRegistration
from schemas.user_schema import UserCreate
from utils.hash_password import hash_password, verify_password
from utils.otp_store import is_verified

from utils.jwt import create_access_token, create_refresh_token


# ------------------------------------------------------------------
# Generate sequential inv_reg_id like I0001, I0002, I0003...
# ------------------------------------------------------------------
def generate_inv_reg_id(db: Session):
    last_user = (
        db.query(UserRegistration)
        .order_by(UserRegistration.id.desc())
        .first()
    )

    # If no users exist
    if not last_user or not last_user.inv_reg_id:
        return "I0001"

    last_id = last_user.inv_reg_id  # ex: I0005

    # Ensure ID format is correct
    if not last_id.startswith("I") or not last_id[1:].isdigit():
        return "I0001"

    number = int(last_id[1:])
    new_number = number + 1

    return f"I{new_number:04d}"


# ------------------------------------------------------------------
# Register User
# ------------------------------------------------------------------
def register_user(db: Session, data: UserCreate):

    # Check email exists
    if db.query(UserRegistration).filter(UserRegistration.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Check mobile exists
    if db.query(UserRegistration).filter(UserRegistration.mobile == data.mobile).first():
        raise HTTPException(status_code=400, detail="Mobile already registered")

    hashed_pwd = hash_password(data.password)

<<<<<<< HEAD
=======
    # Generate sequential inv_reg_id
    new_inv_reg_id = generate_inv_reg_id(db)

    # Create user record
>>>>>>> main
    user = UserRegistration(
        first_name=data.first_name,
        last_name=data.last_name,        # <-- FIXED: was incorrectly using first_name
        email=data.email,
        mobile=data.mobile,
        password=hashed_pwd,
<<<<<<< HEAD
        gender_id=data.gender_id,
        age=data.age,
        dob=data.dob,
        inv_reg_id=data.inv_reg_id,
        role_id=data.role_id,
        created_by=1,
=======
        # gender_id=data.gender_id,
        # age=data.age,
        # dob=data.dob,
        inv_reg_id=new_inv_reg_id,
        role_id=1,                      
        # created_by=1
>>>>>>> main
    )

    db.add(user)
    db.commit()
    db.refresh(user)

<<<<<<< HEAD
    return {"message": "User registered successfully", "user_id": user.id}


# =====================================================
# LOGIN WITH OTP VERIFICATION CHECK
# =====================================================
=======
    return user   # FastAPI returns this through UserResponse schema

>>>>>>> main

# ------------------------------------------------------------------
# Login User
# ------------------------------------------------------------------
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

<<<<<<< HEAD
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
=======
    # Query user by email OR inv_reg_id
    if data.email:
        user = db.query(UserRegistration).filter(UserRegistration.email == data.email).first()
    else:
        user = db.query(UserRegistration).filter(UserRegistration.inv_reg_id == data.inv_reg_id).first()
>>>>>>> main

    # ❌ User not found
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

<<<<<<< HEAD
    # ❌ OTP NOT VERIFIED → BLOCK LOGIN
    if not is_verified(identifier):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="OTP verification required before login",
        )

    # ❌ Password mismatch
=======
    # ❌ Wrong password
>>>>>>> main
    if not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

<<<<<<< HEAD
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
=======
    # SUCCESS
>>>>>>> main
    return {
        "message": "Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }
<<<<<<< HEAD












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

=======
>>>>>>> main
