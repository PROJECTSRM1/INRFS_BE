from sqlalchemy.orm import Session
from fastapi import HTTPException

from models.generated_models import UserRegistration
from utils.email import send_email
from utils.otp_store import (
    generate_otp,
    verify_otp,
    pop_user_data,
)
from utils.hash_password import hash_password


# --------------------------------------------------
# SEND OTP (NO DB INSERT)
# --------------------------------------------------
def send_otp_service(db: Session, email: str):
    """
    STEP 1:
    - Generate OTP
    - Store OTP in memory (otp_store.py)
    - Send OTP email
    - ❌ NO DB interaction
    """

    otp = generate_otp(email)

    send_email(
        to_email=email,
        subject="OTP Verification – INRFS",
        body=(
            f"Your OTP for email verification is:\n\n"
            f"{otp}\n\n"
            f"This OTP is valid for 5 minutes.\n\n"
            f"Regards,\nINRFS Team"
        ),
    )


    



# VERIFY OTP + CREATE USER (DB INSERT HAPPENS HERE)

def verify_otp_service(db: Session, email: str, otp: str):
    """
    STEP 2:
    - Verify OTP (email + otp only)
    - Fetch stored user data
    - Hash password
    - Create user in DB with ALL fields
    """

    # 1️⃣ Verify OTP
    if not verify_otp(email, otp):
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    # 2️⃣ Fetch stored registration data
    user_data = pop_user_data(email)
    if not user_data:
        raise HTTPException(
            status_code=400,
            detail="Registration data expired. Please register again."
        )

    # 3️⃣ Prevent duplicate registration
    if db.query(UserRegistration).filter(
        UserRegistration.email == email
    ).first():
        raise HTTPException(
            status_code=400,
            detail="User already registered"
        )

    # 4️⃣ Hash password (🔥 correct place 🔥)
    user_data["password"] = hash_password(user_data["password"])

    # 5️⃣ Generate Investor Registration ID (lazy import avoids circular import)
    from services.user_service import generate_inv_reg_id

    inv_reg_id = None
    if user_data["role_id"] == 1:
        inv_reg_id = generate_inv_reg_id(db)

    # 6️⃣ Create user with ALL required fields
    user = UserRegistration(
        first_name=user_data["first_name"],
        last_name=user_data["last_name"],
        email=user_data["email"],
        mobile=user_data["mobile"],
        password=user_data["password"],      # ✅ hashed
        gender_id=user_data["gender_id"],
        age=user_data["age"],
        dob=user_data["dob"],
        inv_reg_id=inv_reg_id,
        role_id=user_data["role_id"],
        is_verified=True,
        created_by=1,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # 7️⃣ Confirmation Email (DO NOT BREAK API IF EMAIL FAILS)
    try:
        send_email(
            to_email=user.email,
            subject="Registration Successful – INRFS",
            body=(
                f"Dear {user.first_name},\n\n"
                f"Your registration is complete.\n\n"
                f"Customer-ID: {user.inv_reg_id}\n\n"
                f"You can now login.\n\n"
                f"Regards,\nINRFS Team"
            ),
        )
    except Exception as e:
        # Email failure should NOT affect registration
        print("Email sending failed:", str(e))

    return {
        "message": "OTP verified and user registered successfully",
        "user_id": user.id,
        "inv_reg_id": user.inv_reg_id,
    }
