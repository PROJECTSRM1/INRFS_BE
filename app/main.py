from fastapi import FastAPI
from core.database import Base, engine

from models import plan as plan_model

from routes import user
from routes import plan


Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(user.router)
app.include_router(plan.router)
