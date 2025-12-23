from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

# load env file
load_dotenv()

# Read full URL directly (already encoded)
DATABASE_URL = os.getenv("DATABASE_URL")

print("USING DATABASE_URL =", DATABASE_URL)  # TEMP for debugging

# Create engine
engine = create_engine(DATABASE_URL)

# Session and Base
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
