from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import user
from core.database import Base, engine

from models import plan as plan_model

from routes import user
from routes import plan


Base.metadata.create_all(bind=engine)

app = FastAPI()

# ---------------------------
# CORS CONFIGURATION
# ---------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# ROUTES
# ---------------------------
app.include_router(user.router)
app.include_router(plan.router)


# from fastapi import FastAPI
# from routes import user
# from core.database import Base, engine

# # ❗ DO NOT CREATE TABLES when using read-only DB
# # Base.metadata.create_all(bind=engine)

# app = FastAPI()

# app.include_router(user.router)
