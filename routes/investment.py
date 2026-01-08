from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from services.investment_service import get_my_investments

from fastapi import UploadFile, File, Form
from datetime import date
from decimal import Decimal


from core.database import get_db
from schemas.investment_schema import InvestmentCreate, InvestmentUpdate
from services.investment_service import (
    create_investment,
    get_all_investments,
    get_investment,
    update_investment,
    delete_investment,
    get_status
)
from utils.auth import get_current_user
#from utils.jwt import get_current_user   # ✅ FIXED
from models.generated_models import UserRegistration

router = APIRouter(
    prefix="/investments",
    tags=["Investments"]
)

# ---------------- CREATE ----------------
@router.post("/")
def create(
    principal_amount: Decimal = Form(...),
    plan_type_id: int = Form(...),
    maturity_date: date = Form(...),
    upload_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserRegistration = Depends(get_current_user)
):
    payload = InvestmentCreate(
        principal_amount=principal_amount,
        plan_type_id=plan_type_id,
        maturity_date=maturity_date,
        upload_file=upload_file
    )

    return create_investment(db, payload, current_user.id)

# ---------------- GET ALL ----------------
@router.get("/")
def get_all(
    db: Session = Depends(get_db),
    current_user: UserRegistration = Depends(get_current_user)
):
    return get_all_investments(db)


# ---------------- GET MY INVESTMENTS ----------------
@router.get("/my")
def get_my(
    db: Session = Depends(get_db),
    current_user: UserRegistration = Depends(get_current_user)
):
    return get_my_investments(db, current_user.id)


# ---------------- READ ONE ----------------
@router.get("/{investment_id}")
def get_one(
    investment_id: int,
    db: Session = Depends(get_db),
):
    inv = get_investment(db, investment_id)
    return {
        "created_by": inv.created_by,
        "investment_id": inv.id,
        "status": get_status(inv)
    }


# ---------------- UPDATE ----------------
@router.put("/{investment_id}")
def update(
    investment_id: int,
    payload: InvestmentUpdate = Body(...),
    db: Session = Depends(get_db)
):

    inv = update_investment(db, investment_id, payload)
    return {
        "created_by": inv.created_by,
        "investment_id": inv.id,
        "status": get_status(inv)
    }


# ---------------- DELETE ----------------
@router.delete("/{investment_id}")
def delete(
    investment_id: int,
    db: Session = Depends(get_db),
):

    return delete_investment(db, investment_id)

