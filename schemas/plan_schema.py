from pydantic import BaseModel
from typing import Optional


# ======================
# CREATE
# ======================
class PlanCreate(BaseModel):
    plan_type: str
    percentage: str
    returns_in_days: str
    is_active: Optional[bool] = True


# ======================
# UPDATE
# ======================
class PlanUpdate(BaseModel):
    plan_type: Optional[str] = None
    percentage: Optional[str] = None
    returns_in_days: Optional[str] = None
    is_active: Optional[bool] = None


# ======================
# RESPONSE
# ======================
class PlanResponse(BaseModel):
    id: int
    plan_type: str
    percentage: str
    returns_in_days: str
    is_active: bool

    class Config:
        from_attributes = True
