from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.generated_models import UserRegistration
from utils.email import send_email
from utils.otp_store import generate_otp, verify_otp, mark_verified


# -----------------------------
# Send OTP
# -----------------------------
def send_otp_service(db: Session, email: str):
    user = db.query(UserRegistration).filter(
        UserRegistration.email == email
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    otp = generate_otp(email)

    send_email(
        to_email=email,
        subject="OTP Verification – INRFS",
        body=(
            f"Dear {user.first_name},\n\n"
            f"Your OTP is: {otp}\n"
            f"Investor Registration ID: {user.inv_reg_id}\n\n"
            f"This OTP is valid for 5 minutes.\n\n"
            f"Regards,\nINRFS Team"
        ),
    )

    return {"message": "OTP sent successfully"}


# -----------------------------
# Verify OTP  ✅ FIXED
# -----------------------------
def verify_otp_service(db: Session, email: str, otp: str):
    user = db.query(UserRegistration).filter(
        UserRegistration.email == email
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_otp(email, otp):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP",
        )

    # ✅ Mark BOTH identifiers as verified
    mark_verified(user.email)
    mark_verified(user.inv_reg_id)

    return {"message": "Email verified successfully"}




# from sqlalchemy.orm import Session
# from fastapi import HTTPException, status

# from models.generated_models import UserRegistration
# from utils.email import send_email
# from utils.otp_store import generate_otp, verify_otp

# from utils.otp_store import verify_otp, mark_verified

# def send_otp_service(db: Session, email: str):
#     user = db.query(UserRegistration).filter(
#         UserRegistration.email == email
#     ).first()

#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     otp = generate_otp(email)

#     send_email(
#         to_email=email,
#         subject="OTP Verification – INRFS",
#         body=(
#             f"Dear {user.first_name},\n\n"
#             f"Your OTP is: {otp}\n"
#             f"Investor Registration ID: {user.inv_reg_id}\n\n"
#             f"This OTP is valid for 5 minutes.\n\n"
#             f"Regards,\nINRFS Team"
#         ),
#     )

#     return {"message": "OTP sent successfully"}



# def verify_otp_service(email: str, otp: str):
#     if not verify_otp(email, otp):
#         raise HTTPException(status_code=400, detail="Invalid or expired OTP")

#     mark_verified(email)

#     return {"message": "Email verified successfully"}

