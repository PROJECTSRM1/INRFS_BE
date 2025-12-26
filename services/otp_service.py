from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.generated_models import UserRegistration
from utils.email import send_email
from utils.otp_store import generate_otp, verify_otp, mark_verified


# -----------------------------
# SEND OTP (called internally)
# -----------------------------
def send_otp_service(db: Session, email: str):
    user = db.query(UserRegistration).filter(
        UserRegistration.email == email
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    otp = generate_otp(email)

    # 📩 OTP EMAIL
    send_email(
        to_email=email,
        subject="OTP Verification – INRFS",
        body=(
            f"Dear {user.first_name},\n\n"
            f"Your OTP for email verification is:\n\n"
            f"{otp}\n\n"
            # f"Investor Registration ID: {user.inv_reg_id}\n\n"
            f"This OTP is valid for 5 minutes.\n\n"
            f"Regards,\nINRFS Team"
        ),
    )


# -----------------------------
# VERIFY OTP + THANK YOU EMAIL
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

    # ✅ Mark BOTH identifiers verified
    mark_verified(user.email)
    mark_verified(user.inv_reg_id)

    # 📩 THANK YOU EMAIL
    send_email(
        to_email=user.email,
        subject="Registration Successful – INRFS",
        body=(
            f"Dear {user.first_name},\n\n"
            f"Thank you for registering with INRFS.\n\n"
            f"Your registration has been successfully completed.\n\n"
            f"Investor Registration ID: {user.inv_reg_id}\n\n"
            f"You can now log in using your Email ID or "
            f"Investor Registration ID along with your password.\n\n"
            f"Regards,\nINRFS Team"
        ),
    )

    return {
        "message": "OTP verified successfully. Confirmation email sent."
    }






















# from sqlalchemy.orm import Session
# from fastapi import HTTPException, status

# from models.generated_models import UserRegistration
# from utils.email import send_email
# from utils.otp_store import generate_otp, verify_otp, mark_verified


# # -----------------------------
# # Send OTP
# # -----------------------------
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


# # -----------------------------
# # Verify OTP  ✅ FIXED
# # -----------------------------
# def verify_otp_service(db: Session, email: str, otp: str):
#     user = db.query(UserRegistration).filter(
#         UserRegistration.email == email
#     ).first()

#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     if not verify_otp(email, otp):
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invalid or expired OTP",
#         )

#     # ✅ Mark BOTH identifiers as verified
#     mark_verified(user.email)
#     mark_verified(user.inv_reg_id)

#     return {"message": "Email verified successfully"}


