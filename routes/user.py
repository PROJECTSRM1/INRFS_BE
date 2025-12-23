from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_db
# from models.user import User
from models.generated_models import UserRegistration

from services.user_service import register_user, login_user
from schemas.user_schema import UserCreate 


router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register")
def register(data: UserCreate, db: Session = Depends(get_db)):
    return register_user(db, data)
