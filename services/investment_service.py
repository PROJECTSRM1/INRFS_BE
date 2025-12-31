from sqlalchemy.orm import Session
from sqlalchemy import update,text
from fastapi import HTTPException
from decimal import Decimal, InvalidOperation
import datetime

from models.generated_models import InvConfig, MasterPlanType


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


# ---------------- CREATE ----------------

def create_investment(db: Session, data):
    plan = db.query(MasterPlanType).filter(
        MasterPlanType.id == data.plan_type_id,
        MasterPlanType.is_active == True
    ).first()

    if not plan:
        raise HTTPException(status_code=400, detail="Invalid plan type")

    percentage = parse_percentage(plan.percentage)
    interest = calculate_interest(data.principal_amount, percentage)
    maturity_amount = data.principal_amount + interest

    # -------- INSERT FIRST --------
    inv = InvConfig(
        principal_amount=data.principal_amount,
        plan_type_id=data.plan_type_id,
        interest_amount=interest,
        maturity_amount=maturity_amount,
        maturity_date=data.maturity_date,
        uk_inv_id=data.uk_inv_id,
        created_by=data.customer_id,
        is_active=True
    )

    db.add(inv)
    db.commit()
    db.refresh(inv)

    # -------- FORCE UPDATE USING RAW SQL (IMPORTANT) --------
    db.execute(
    text("""
    UPDATE inv_config
    SET created_by = :created_by,
        created_date = :created_date
    WHERE id = :id
    """),
    {
        # ✅ fallback logic HERE (not in schema)
        "created_by": (
            data.created_by
            if data.created_by is not None
            else data.customer_id
        ),
        "created_date": (
            data.created_date
            if data.created_date is not None
            else datetime.datetime.utcnow()
        ),
        "id": inv.id
    }
)
    db.commit()


    return {
    "customer_id": (
        data.created_by
        if data.created_by is not None
        else data.customer_id
    ),
    "investment_id": inv.id,
    "status": get_status(inv)
}



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
