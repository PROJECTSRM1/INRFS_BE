from pydantic import BaseModel
from typing import Optional


class PlanCreate(BaseModel):
    name: str
    returns_percentage: float
    duration_months: int
    description: Optional[str] = None


class PlanUpdate(BaseModel):
    returns_percentage: Optional[float]
    duration_months: Optional[int]
    description: Optional[str]
    is_active: Optional[bool]


class PlanResponse(BaseModel):
    id: int
    name: str
    returns_percentage: float
    duration_months: int
    description: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True
