# from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
# from sqlalchemy.sql import func
# from core.database import Base


# class Plan(Base):
#     __tablename__ = "plans"

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, nullable=False, unique=True)
#     returns_percentage = Column(Float, nullable=False)
#     duration_months = Column(Integer, nullable=False)
#     description = Column(String, nullable=True)
#     is_active = Column(Boolean, default=True)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())
