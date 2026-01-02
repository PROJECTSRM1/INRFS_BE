from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from schemas.plan_schema import (
    PlanCreate,
    PlanUpdate,
    PlanResponse
)
from services.plan_service import (
    create_plan,
    get_all_plans,
    get_plan_by_id,
    update_plan,
    delete_plan
)

router = APIRouter(prefix="/plans", tags=["Plans"])


@router.post("/", response_model=PlanResponse)
def create(data: PlanCreate, db: Session = Depends(get_db)):
    return create_plan(db, data)


@router.get("/", response_model=list[PlanResponse])
def list_all(db: Session = Depends(get_db)):
    return get_all_plans(db)


@router.get("/{plan_id}", response_model=PlanResponse)
def get_one(plan_id: int, db: Session = Depends(get_db)):
    return get_plan_by_id(db, plan_id)


@router.put("/{plan_id}", response_model=PlanResponse)
def update(plan_id: int, data: PlanUpdate, db: Session = Depends(get_db)):
    return update_plan(db, plan_id, data)


@router.delete("/{plan_id}")
def delete(plan_id: int, db: Session = Depends(get_db)):
    return delete_plan(db, plan_id)
