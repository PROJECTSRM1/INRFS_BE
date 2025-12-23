from fastapi import FastAPI
from routes import user
from core.database import Base, engine

# ❗ DO NOT CREATE TABLES when using read-only DB
# Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(user.router)
