from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import HTTPException
from decimal import Decimal, InvalidOperation
import datetime

from models.generated_models import InvConfig, MasterPlanType, UserRegistration
from services.email_templates import investment_created_email
from utils.email import send_email
from utils.storage import store_file




# ---------------- HELPERS ----------------

def parse_percentage(value: str) -> Decimal:
    try:
        clean = value.replace('%', '').strip()
        return Decimal(clean)
    except InvalidOperation:
        raise HTTPException(
            status_code=500,
            detail=f"Invalid percentage value in DB: {value}"
        )


def calculate_interest(amount: Decimal, percentage: Decimal) -> Decimal:
    return (amount * percentage) / Decimal(100)


def get_status(inv: InvConfig) -> str:
    today = datetime.date.today()

    if inv.is_active is False:
        return "inactive"
    if inv.maturity_date < today:
        return "completed"
    return "active"


def generate_uk_inv_id(db: Session) -> str:
    last = db.query(InvConfig).order_by(InvConfig.id.desc()).first()

    if not last or not last.uk_inv_id:
        return "INV0001"

    digits = "".join(filter(str.isdigit, last.uk_inv_id))

    if not digits:
        return "INV0001"

    num = int(digits)
    return f"INV{num + 1:04d}"



# ---------------- CREATE ----------------

def create_investment(db: Session, data, user_id: int):

    plan = db.query(MasterPlanType).filter(
        MasterPlanType.id == data.plan_type_id,
        MasterPlanType.is_active == True
    ).first()

    if not plan:
        raise HTTPException(status_code=400, detail="Invalid plan type")

    percentage = parse_percentage(plan.percentage)
    interest = calculate_interest(data.principal_amount, percentage)
    maturity_amount = data.principal_amount + interest

    uk_inv_id = generate_uk_inv_id(db)
    
    file_url = store_file(data.upload_file)


    inv = InvConfig(
        principal_amount=data.principal_amount,
        plan_type_id=data.plan_type_id,
        interest_amount=interest,
        maturity_amount=maturity_amount,
        maturity_date=data.maturity_date,
        uk_inv_id=uk_inv_id,
        upload_file=file_url,
        created_by=user_id,
        is_active=True
    )

    # ✅ SAVE INVESTMENT
    db.add(inv)
    db.commit()
    db.refresh(inv)

    # ✅ FETCH USER
    user = db.query(UserRegistration).filter(
        UserRegistration.id == user_id
    ).first()

    if user and user.email:
        invest_datetime = inv.created_date or datetime.datetime.utcnow()
        invest_date = invest_datetime.strftime("%d-%m-%Y")
        invest_time = invest_datetime.strftime("%I:%M %p")

        tenure_days = (inv.maturity_date - invest_datetime.date()).days

        try:
            subject, body = investment_created_email(
                user_name=user.first_name,
                uk_inv_id=inv.uk_inv_id,
                invest_date=invest_date,
                invest_time=invest_time,
                tenure_days=tenure_days
            )

            send_email(
                to_email=user.email,
                subject=subject,
                body=body
            )

            print(f"✅ Investment email sent to {user.email}")

        except Exception as e:
            print("❌ Investment email failed:", e)

    else:
        print("⚠️ User email not found, skipping email")

    # ✅ RETURN MUST BE INSIDE FUNCTION
    return {
        "customer_id": user_id,
        "investment_id": inv.id,
        "status": get_status(inv),
        "uk_inv_id": inv.uk_inv_id
    }




# ---------------- READ ALL ----------------

# ---------------- READ ALL (BY LOGGED-IN USER) ----------------
def get_all_investments(db: Session, user_id: int):
    return db.query(InvConfig).all()

# ---------------- READ MY INVESTMENTS ----------------
def get_my_investments(db: Session, user_id: int):
    return (
        db.query(InvConfig)
        .filter(InvConfig.created_by == user_id)
        .order_by(InvConfig.id.asc())
        .all()
    )

        
        
    



# ---------------- READ ONE ----------------

def get_investment(db: Session, investment_id: int):
    inv = db.query(InvConfig).filter(
        InvConfig.id == investment_id
    ).first()

    if not inv:
        raise HTTPException(status_code=404, detail="Investment not found")

    return inv


# ---------------- READ BY CUSTOMER ----------------

def get_investments_by_customer(db: Session, customer_id: int):
    return db.query(InvConfig).filter(
        InvConfig.created_by == customer_id
    ).all()


# ---------------- UPDATE ----------------

def update_investment(db: Session, investment_id: int, data):
    inv = get_investment(db, investment_id)

    if data.principal_amount is not None:
        inv.principal_amount = data.principal_amount

    if data.plan_type_id is not None:
        inv.plan_type_id = data.plan_type_id

    if data.maturity_date is not None:
        inv.maturity_date = data.maturity_date

    if data.is_active is not None:
        inv.is_active = data.is_active

    inv.modified_date = datetime.datetime.utcnow()

    db.commit()
    db.refresh(inv)

    return inv


# ---------------- DELETE (SOFT DELETE) ----------------

def delete_investment(db: Session, investment_id: int):
    inv = get_investment(db, investment_id)

    inv.is_active = False
    inv.modified_date = datetime.datetime.utcnow()

    db.commit()

    return {"message": "Investment deactivated successfully"}
