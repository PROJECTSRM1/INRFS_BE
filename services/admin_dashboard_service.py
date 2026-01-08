from sqlalchemy.orm import Session
from sqlalchemy import func

from models.generated_models import (
    UserRegistration,
    InvConfig,
    MasterPlanType
)

# --------------------------------------------------
# ADMIN DASHBOARD DATA (PLAN-BASED)
# --------------------------------------------------
def get_admin_dashboard_data(
    db: Session,
    plan_type_id: int | None = None
):
    # -----------------------------
    # BASE INVESTMENT QUERY
    # -----------------------------
    inv_query = db.query(InvConfig)

    if plan_type_id:
        inv_query = inv_query.filter(
            InvConfig.plan_type_id == plan_type_id
        )

    # -----------------------------
    # KPI METRICS
    # -----------------------------
    total_investors = db.query(UserRegistration).filter(
        UserRegistration.role_id == 1
    ).count()

    active_investments = inv_query.filter(
        InvConfig.is_active == True
    ).count()

    totals = inv_query.with_entities(
        func.coalesce(func.sum(InvConfig.principal_amount), 0),
        func.coalesce(func.sum(InvConfig.interest_amount), 0)
    ).first()

    total_invested = totals[0]
    interest_payable = totals[1]

    # -----------------------------
    # PLAN / TENURE DISTRIBUTION
    # -----------------------------
    plan_distribution = (
        db.query(
            MasterPlanType.id,
            MasterPlanType.plan_type,
            MasterPlanType.duration,
            func.count(InvConfig.id)
        )
        .join(InvConfig, InvConfig.plan_type_id == MasterPlanType.id)
        .group_by(
            MasterPlanType.id,
            MasterPlanType.plan_type,
            MasterPlanType.duration
        )
        .all()
    )

    plan_data = [
        {
            "plan_type_id": pid,
            "plan_type": plan,
            "duration": duration,
            "investment_count": count
        }
        for pid, plan, duration, count in plan_distribution
    ]

    return {
        "summary": {
            "total_investors": total_investors,
            "active_investments": active_investments,
            "total_invested": float(total_invested),
            "interest_payable": float(interest_payable),
        },
        "plan_distribution": plan_data,
        "filters": {
            "plan_type_id": plan_type_id
        }
    }
