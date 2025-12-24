from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.generated_models import UserRegistration
from utils.email import send_email
from utils.otp_store import generate_otp, verify_otp


def send_otp_service(db: Session, email: str):
    user = db.query(UserRegistration).filter(
        UserRegistration.email == email
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    otp = generate_otp(email)

    send_email(
        to_email=email,
        subject="Your OTP Verification Code",
        body=f"Your OTP is {otp}. It is valid for 5 minutes.",
    )

    return {"message": "OTP sent successfully"}


def verify_otp_service(email: str, otp: str):
    if not verify_otp(email, otp):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP",
        )

    return {"message": "Email verified successfully"}
