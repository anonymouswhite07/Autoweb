from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from .database import Base

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True)
    description = Column(String)
    rating = Column(String)
    instructor = Column(String)
    coupon = Column(String, nullable=True)
    image = Column(String, nullable=True)
    udemy_link = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
