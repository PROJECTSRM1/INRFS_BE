from sqlalchemy.orm import Session
from fastapi import HTTPException

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
    user = db.query(UserRegistration).filter(
        UserRegistration.email == data.email
    ).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    # Compare hashed password
    if not verify_password(data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    return {"message": "Login successful", "user_id": user.id}
