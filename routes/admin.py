from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db
from utils.auth import get_current_user
from models.generated_models import UserRegistration
from services.admin_dashboard_service import get_admin_dashboard_data

router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])

@router.get("/dashboard")
def admin_dashboard(
    plan_type_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: UserRegistration = Depends(get_current_user),
):
    # 🔐 ONLY ADMIN & SUPER ADMIN
    if current_user.role_id not in (2, 3):
        raise HTTPException(status_code=403, detail="Admin access required")

    return get_admin_dashboard_data(
        db=db,
        plan_type_id=plan_type_id
    )
