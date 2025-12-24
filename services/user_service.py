from sqlalchemy.orm import Session
from fastapi import HTTPException, status


from models.generated_models import UserRegistration
from schemas.user_schema import UserCreate
from utils.hash_password import hash_password, verify_password


def register_user(db: Session, data: UserCreate):
    # Check email exists
    if db.query(UserRegistration).filter(UserRegistration.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Check mobile exists
    if db.query(UserRegistration).filter(UserRegistration.mobile == data.mobile).first():
        raise HTTPException(status_code=400, detail="Mobile already registered")

    # Hash password
    hashed_pwd = hash_password(data.password)

    # Create user
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
        created_by=1
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "User registered successfully", "user_id": user.id}






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

    # ✅ Query by email OR inv_reg_id
    if data.email:
        user = (
            db.query(UserRegistration)
            .filter(UserRegistration.email == data.email)
            .first()
        )
    else:
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

    # ❌ Password mismatch (hashed)
    if not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # ✅ Success
    return {
        "message": "Login successful",
        "user_id": user.id,
        "inv_reg_id": user.inv_reg_id,
    }

