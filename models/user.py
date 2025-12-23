from sqlalchemy import Column, Integer, String, Boolean
from core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String, unique=True, index=True) 
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    mobile = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

    # OTP fields
    email_otp = Column(String, nullable=True)
    mobile_otp = Column(String, nullable=True)

    is_email_verified = Column(Boolean, default=False)
    is_mobile_verified = Column(Boolean, default=False)
