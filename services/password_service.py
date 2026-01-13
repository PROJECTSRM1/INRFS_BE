from fastapi import HTTPException
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from models.generated_models import UserRegistration
from utils.jwt import create_reset_password_token, SECRET_KEY, ALGORITHM
from utils.hash_password import hash_password
from utils.email import send_email

import os
from dotenv import load_dotenv

# load env file
load_dotenv()

# -------------------------
# FORGOT PASSWORD
# -------------------------

def forgot_password_service(db: Session, email: str):
    user = db.query(UserRegistration).filter(
        UserRegistration.email == email,
        UserRegistration.is_active == True
    ).first()

    # Always return same message (security)
    response = {
        "message": "If the email exists, a reset link has been sent"
    }

    if not user:
        return response

    token = create_reset_password_token(email)

    FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL")
    reset_link = f"{FRONTEND_BASE_URL}/reset-password?token={token}"

    send_email(
        to_email=email,
        subject="Reset Your Password – INRFS",
        body=(
            f"Dear {user.first_name},\n\n"
            f"Click the link below to reset your password:\n\n"
            f"{reset_link}\n\n"
            f"This link is valid for 15 minutes.\n\n"
            f"Regards,\nINRFS Team"
        ),
    )

    # 🔥 ADD TOKEN TO RESPONSE (DEV / TEST ONLY)
    response["reset_token"] = token

    return response



# -------------------------
# RESET PASSWORD
# -------------------------
def reset_password_service(db: Session, token: str, new_password: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # -------------------------
        # TOKEN TYPE CHECK
        # -------------------------
        if payload.get("type") != "password_reset":
            raise HTTPException(status_code=400, detail="Invalid token")

        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=400, detail="Invalid token payload")

        # -------------------------
        # FETCH ACTIVE USER
        # -------------------------
        user = db.query(UserRegistration).filter(
            UserRegistration.email == email,
            UserRegistration.is_active == True
        ).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # -------------------------
        # UPDATE PASSWORD
        # -------------------------
        user.password = hash_password(new_password)

        # -------------------------
        # ✅ AUTO-VERIFY INVESTORS ONLY
        # -------------------------
        if user.role_id == 1:
            user.is_verified = True

        db.commit()

        return {"message": "Password reset successful"}

    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")



