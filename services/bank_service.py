from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.generated_models import UserRegistration


def add_or_update_bank_details(
    db: Session,
    user_id: int,
    bank_id: int,
    # bank_account_no: int,
    bank_account_no: str,
    ifsc_code: str,
):
    user = db.query(UserRegistration).filter(
        UserRegistration.id == user_id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Complete OTP verification before adding bank details",
        )

    user.bank_id = bank_id
    # user.bank_account_no = bank_account_no
    user.bank_account_no = str(bank_account_no)  # ✅ FORCE STRING
    user.ifsc_code = ifsc_code

    db.commit()
    db.refresh(user)

    return {
        "message": "Bank details updated successfully",
        "bank_id": user.bank_id,
        "bank_account_no": user.bank_account_no,
        "ifsc_code": user.ifsc_code,
    }


def get_bank_details(db: Session, user_id: int):
    user = db.query(UserRegistration).filter(
        UserRegistration.id == user_id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "bank_id": user.bank_id,
        "bank_account_no": user.bank_account_no,
        "ifsc_code": user.ifsc_code,
        "is_verified": user.is_verified,
    }
