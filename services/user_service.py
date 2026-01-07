from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.generated_models import UserRegistration
from schemas.user_schema import UserCreate
from utils.hash_password import hash_password, verify_password
from utils.jwt import create_access_token, create_refresh_token
from services.otp_service import send_otp_service

from sqlalchemy import func
from models.generated_models import InvConfig

# -----------------------------
# Generate inv_reg_id
# -----------------------------

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

    number = int(last_id[1:])
    return f"I{number + 1:04d}"











# def generate_inv_reg_id(db: Session):
#     last_user = (
#         db.query(UserRegistration)
#         .order_by(UserRegistration.id.desc())
#         .first()
#     )

#     if not last_user or not last_user.inv_reg_id:
#         return "I0001"

#     last_id = last_user.inv_reg_id  # e.g. I0005

#     if not last_id.startswith("I") or not last_id[1:].isdigit():
#         return "I0001"

#     number = int(last_id[1:])
#     return f"I{number + 1:04d}"















# -----------------------------
# REGISTER USER (AUTO OTP)
# -----------------------------

def register_user(db: Session, data: UserCreate):

    # -------------------------
    # ROLE VALIDATION
    # -------------------------
    if data.role_id not in (1, 2, 3):
        raise HTTPException(
            status_code=400,
            detail="Invalid role_id"
        )

    # ❗ OPTIONAL SECURITY (recommended)
    # Block public creation of Admins
    # if data.role_id in (2, 3):
    #     raise HTTPException(
    #         status_code=403,
    #         detail="Admin creation is not allowed via public registration"
    #     )

    # -------------------------
    # DUPLICATE CHECKS
    # -------------------------
    if db.query(UserRegistration).filter(
        UserRegistration.email == data.email
    ).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    if db.query(UserRegistration).filter(
        UserRegistration.mobile == data.mobile
    ).first():
        raise HTTPException(status_code=400, detail="Mobile already registered")

    # -------------------------
    # PASSWORD HASH
    # -------------------------
    hashed_pwd = hash_password(data.password)

    # -------------------------
    # INV_REG_ID LOGIC
    # -------------------------
    inv_reg_id = None

    if data.role_id == 1:
        inv_reg_id = generate_inv_reg_id(db)

    # -------------------------
    # CREATE USER
    # -------------------------
    user = UserRegistration(
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        mobile=data.mobile,
        password=hashed_pwd,
        gender_id=data.gender_id,
        age=data.age,
        dob=data.dob,
        inv_reg_id=inv_reg_id,     # ✅ NULL for Admins
        role_id=data.role_id,
        created_by=1,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # -------------------------
    # OTP ONLY FOR INVESTORS
    # -------------------------
    if data.role_id == 1:
        send_otp_service(db, user.email)

    return {
        "message": "User registered successfully",
        "user_id": user.id,
        "inv_reg_id": user.inv_reg_id,  # null for Admins
        "role_id": user.role_id
    }





















# def register_user(db: Session, data: UserCreate):

#     # 🔒 Allow ONLY normal users here
#     if data.role_id != 1:
#         raise HTTPException(
#             status_code=403,
#             detail="Only normal users can register here"
#         )

#     # Email already exists
#     if db.query(UserRegistration).filter(
#         UserRegistration.email == data.email
#     ).first():
#         raise HTTPException(status_code=400, detail="Email already registered")

#     # Mobile already exists
#     if db.query(UserRegistration).filter(
#         UserRegistration.mobile == data.mobile
#     ).first():
#         raise HTTPException(status_code=400, detail="Mobile already registered")

#     hashed_pwd = hash_password(data.password)
#     new_inv_reg_id = generate_inv_reg_id(db)

#     user = UserRegistration(
#         first_name=data.first_name,
#         last_name=data.last_name,
#         email=data.email,
#         mobile=data.mobile,
#         password=hashed_pwd,
#         gender_id=data.gender_id,
#         age=data.age,
#         dob=data.dob,
#         inv_reg_id=new_inv_reg_id,
#         role_id=data.role_id,   # ✅ comes from request
#         created_by=1,
#     )

#     db.add(user)
#     db.commit()
#     db.refresh(user)

#     # ✅ Auto send OTP
#     send_otp_service(db, user.email)

#     return {
#         "message": "User registered successfully. OTP sent to email.",
#         "user_id": user.id,
#         "inv_reg_id": user.inv_reg_id,
#     }











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

    # -------------------------
    # FETCH USER
    # -------------------------
    if data.inv_reg_id:
        user = db.query(UserRegistration).filter(
            UserRegistration.inv_reg_id == data.inv_reg_id
        ).first()

        if user and user.role_id != 1:
            raise HTTPException(
                status_code=400,
                detail="inv_reg_id login allowed only for investors"
            )

    else:  # email login
        user = db.query(UserRegistration).filter(
            UserRegistration.email == data.email
        ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
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
    # JWT TOKENS
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
#         UserRegistration.inv_reg_id == data.inv_reg_id
#     ).first()

#     if user and user.role_id != 1:
#         raise HTTPException(
#             status_code=400,
#             detail="inv_reg_id login allowed only for investors"
#         )

#     # if data.email:
#     #     user = db.query(UserRegistration).filter(
#     #         UserRegistration.email == data.email
#     #     ).first()
# #

#     else:
#         user = db.query(UserRegistration).filter(
#             UserRegistration.inv_reg_id == data.inv_reg_id
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

#     # if not user.is_verified:
#     #     raise HTTPException(
#     #         status_code=status.HTTP_403_FORBIDDEN,
#     #         detail="OTP verification required before login",
#     #     )

#     if not verify_password(data.password, user.password):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid credentials",
#         )
    


#     access_token = create_access_token({
#     "sub": user.inv_reg_id,   # 🔑 PRIMARY IDENTITY
#     "user_id": user.id,       # optional (DB joins)
#     "role_id": user.role_id
# })

#     refresh_token = create_refresh_token({
#     "sub": user.inv_reg_id,
#     "user_id": user.id,
#     "role_id": user.role_id
# })


#     return {
#         "message": "Login successful",
#         "Customer-ID": user.inv_reg_id,
#         "First_Name": user.first_name,
#         "access_token": access_token,
#         "refresh_token": refresh_token,
#         "token_type": "bearer",
#     }



















# -----------------------------
# CRUD OPERATIONS
# -----------------------------

def get_all_users(db: Session):
    users = db.query(UserRegistration).all()
    response = []

    for user in users:
        # base user response (UNCHANGED FIELDS)
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

        # 👇 Add investment data ONLY for investors
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
        else:
            # keep response consistent
            user_data.update({
                "total_principal_amount": None,
                "total_maturity_amount": None,
                "investment_created_date": None,
                "investment_maturity_date": None,
            })

        response.append(user_data)

    return response




# def get_all_users(db: Session):
#     return db.query(UserRegistration).all()




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





























# from sqlalchemy.orm import Session
# from fastapi import HTTPException, status

# from models.generated_models import UserRegistration, InvConfig
# from schemas.user_schema import UserCreate
# from utils.hash_password import hash_password, verify_password
# from utils.jwt import create_access_token, create_refresh_token
# from services.otp_service import send_otp_service

# from sqlalchemy import func


# # -------------------------------------------------
# # Generate inv_reg_id based on role
# # -------------------------------------------------
# def generate_inv_reg_id(db: Session, role_id: int) -> str:
#     """
#     role_id = 1 -> I0001
#     role_id = 2 -> SA0001
#     role_id = 3 -> A0001
#     """

#     if role_id == 1:
#         prefix = "I"
#     elif role_id == 2:
#         prefix = "SA"
#     elif role_id == 3:
#         prefix = "A"
#     else:
#         raise ValueError("Invalid role_id")

#     last_user = (
#         db.query(UserRegistration)
#         .filter(UserRegistration.inv_reg_id.like(f"{prefix}%"))
#         .order_by(UserRegistration.id.desc())
#         .first()
#     )

#     if not last_user:
#         return f"{prefix}0001"

#     last_id = last_user.inv_reg_id.replace(prefix, "")

#     if not last_id.isdigit():
#         return f"{prefix}0001"

#     number = int(last_id)
#     return f"{prefix}{number + 1:04d}"


# # -------------------------------------------------
# # REGISTER USER
# # -------------------------------------------------
# def register_user(db: Session, data: UserCreate):

#     # -------------------------
#     # ROLE VALIDATION
#     # -------------------------
#     if data.role_id not in (1, 2, 3):
#         raise HTTPException(
#             status_code=400,
#             detail="Invalid role_id"
#         )

#     # -------------------------
#     # DUPLICATE CHECKS
#     # -------------------------
#     if db.query(UserRegistration).filter(
#         UserRegistration.email == data.email
#     ).first():
#         raise HTTPException(status_code=400, detail="Email already registered")

#     if db.query(UserRegistration).filter(
#         UserRegistration.mobile == data.mobile
#     ).first():
#         raise HTTPException(status_code=400, detail="Mobile already registered")

#     # -------------------------
#     # PASSWORD HASH
#     # -------------------------
#     hashed_pwd = hash_password(data.password)

#     # -------------------------
#     # GENERATE inv_reg_id (ALL ROLES)
#     # -------------------------
#     inv_reg_id = generate_inv_reg_id(db, data.role_id)

#     # -------------------------
#     # CREATE USER
#     # -------------------------
#     user = UserRegistration(
#         first_name=data.first_name,
#         last_name=data.last_name,
#         email=data.email,
#         mobile=data.mobile,
#         password=hashed_pwd,
#         gender_id=data.gender_id,
#         age=data.age,
#         dob=data.dob,
#         inv_reg_id=inv_reg_id,
#         role_id=data.role_id,
#         created_by=1,
#     )

#     db.add(user)
#     db.commit()
#     db.refresh(user)

#     # -------------------------
#     # OTP ONLY FOR INVESTORS
#     # -------------------------
#     if data.role_id == 1:
#         send_otp_service(db, user.email)

#     return {
#         "message": "User registered successfully",
#         "user_id": user.id,
#         "inv_reg_id": user.inv_reg_id,
#         "role_id": user.role_id
#     }


# # -------------------------------------------------
# # LOGIN USER
# # -------------------------------------------------
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

#     # -------------------------
#     # FETCH USER
#     # -------------------------
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

#     # -------------------------
#     # OTP CHECK (INVESTORS ONLY)
#     # -------------------------
#     if user.role_id == 1 and not user.is_verified:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="OTP verification required before login",
#         )

#     # -------------------------
#     # PASSWORD CHECK
#     # -------------------------
#     if not verify_password(data.password, user.password):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid credentials",
#         )

#     # -------------------------
#     # JWT TOKENS
#     # -------------------------
#     access_token = create_access_token({
#         "sub": user.inv_reg_id,
#         "user_id": user.id,
#         "role_id": user.role_id
#     })

#     refresh_token = create_refresh_token({
#         "sub": user.inv_reg_id,
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


# # -------------------------------------------------
# # GET ALL USERS
# # -------------------------------------------------
# def get_all_users(db: Session):
#     users = db.query(UserRegistration).all()
#     response = []

#     for user in users:
#         user_data = {
#             "id": user.id,
#             "inv_reg_id": user.inv_reg_id,
#             "first_name": user.first_name,
#             "last_name": user.last_name,
#             "email": user.email,
#             "mobile": user.mobile,
#             "role_id": user.role_id,
#             "gender_id": user.gender_id,
#             "age": user.age,
#             "dob": user.dob,
#         }

#         if user.role_id == 1:
#             agg = (
#                 db.query(
#                     func.coalesce(func.sum(InvConfig.principal_amount), 0),
#                     func.coalesce(func.sum(InvConfig.maturity_amount), 0),
#                     func.min(InvConfig.created_date),
#                     func.max(InvConfig.maturity_date),
#                 )
#                 .filter(InvConfig.created_by == user.id)
#                 .first()
#             )

#             user_data.update({
#                 "total_principal_amount": agg[0],
#                 "total_maturity_amount": agg[1],
#                 "investment_created_date": agg[2],
#                 "investment_maturity_date": agg[3],
#             })
#         else:
#             user_data.update({
#                 "total_principal_amount": None,
#                 "total_maturity_amount": None,
#                 "investment_created_date": None,
#                 "investment_maturity_date": None,
#             })

#         response.append(user_data)

#     return response


# # -------------------------------------------------
# # BASIC CRUD
# # -------------------------------------------------
# def get_user_by_id(db: Session, user_id: int):
#     return db.query(UserRegistration).filter(
#         UserRegistration.id == user_id
#     ).first()


# def update_user(db: Session, user_id: int, data):
#     user = get_user_by_id(db, user_id)
#     if not user:
#         return None

#     for field, value in data.dict(exclude_unset=True).items():
#         setattr(user, field, value)

#     db.commit()
#     db.refresh(user)
#     return user


# def delete_user(db: Session, user_id: int):
#     user = get_user_by_id(db, user_id)
#     if not user:
#         return None

#     db.delete(user)
#     db.commit()
#     return True

