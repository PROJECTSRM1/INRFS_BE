from sqlalchemy.orm import Session
from fastapi import HTTPException
from models.plan import Plan
from schemas.plan_schema import PlanCreate, PlanUpdate


def create_plan(db: Session, data: PlanCreate):
    if db.query(Plan).filter(Plan.name == data.name).first():
        raise HTTPException(status_code=400, detail="Plan already exists")

    plan = Plan(**data.dict())
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def get_all_plans(db: Session):
    return db.query(Plan).all()


def get_plan_by_id(db: Session, plan_id: int):
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan


def update_plan(db: Session, plan_id: int, data: PlanUpdate):
    plan = get_plan_by_id(db, plan_id)

    for key, value in data.dict(exclude_unset=True).items():
        setattr(plan, key, value)

    db.commit()
    db.refresh(plan)
    return plan


def delete_plan(db: Session, plan_id: int):
    plan = get_plan_by_id(db, plan_id)
    db.delete(plan)
    db.commit()
    return {"message": "Plan deleted successfully"}
