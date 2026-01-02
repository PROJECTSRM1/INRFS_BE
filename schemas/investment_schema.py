from pydantic import BaseModel, ConfigDict
from typing import Optional
from decimal import Decimal
import datetime


# ---------------- CREATE ----------------
class InvestmentCreate(BaseModel):
    # customer_id: int
    principal_amount: Decimal
    plan_type_id: int
    # uk_inv_id: str                 # bond id
    maturity_date: datetime.date

    # ⚠️ if you REALLY need client input (not recommended)
    created_by: Optional[int] = None
    created_date: Optional[datetime.datetime] = None


# ---------------- UPDATE ----------------
class InvestmentUpdate(BaseModel):
    principal_amount: Optional[Decimal] = None
    plan_type_id: Optional[int] = None
    maturity_date: Optional[datetime.date] = None
    is_active: Optional[bool] = None


# ---------------- RESPONSE ----------------
class InvestmentResponse(BaseModel):
    customer_id: int
    investment_id: int
    status: str
    uk_inv_id: str 
     

    model_config = ConfigDict(from_attributes=True)


# ✅ model_rebuild MUST be OUTSIDE classes
InvestmentCreate.model_rebuild()
InvestmentUpdate.model_rebuild()
InvestmentResponse.model_rebuild()
