from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
load_dotenv()


from routes import user
from core.database import Base, engine


from models import plan as plan_model


from routes import user
from routes import plan
from routes import investment
from routes.payment_routes import router as payment_router
from routes import admin




Base.metadata.create_all(bind=engine)

<<<<<<< HEAD

app = FastAPI(title="Investment Service")

=======
app = FastAPI(title="Investment Service")
>>>>>>> main

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
app.include_router(investment.router)
app.include_router(payment_router)
app.include_router(admin.router)




# from fastapi import FastAPI
# from routes import user
# from core.database import Base, engine


# # ❗ DO NOT CREATE TABLES when using read-only DB
# # Base.metadata.create_all(bind=engine)


# app = FastAPI()


# app.include_router(user.router)

