from pydantic import BaseModel
from typing import Optional


# ======================
# CREATE
# ======================
class PlanCreate(BaseModel):
    plan_type: str
    percentage: str
    duration: str
    is_active: Optional[bool] = True


# ======================
# UPDATE
# ======================
class PlanUpdate(BaseModel):
    plan_type: Optional[str] = None
    percentage: Optional[str] = None
    duration: Optional[str] = None 
    is_active: Optional[bool] = None


# ======================
# RESPONSE
# ======================
class PlanResponse(BaseModel):
    id: int
    plan_type: str
    percentage: str
    duration: str
    is_active: bool
    description: str

    class Config:
        from_attributes = True
