from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4

from app.db.base_class import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    location = Column(String)
    type = Column(String)  # full-time, part-time, contract
    
    description = Column(String, nullable=False)
    requirements = Column(JSON)  # Required and preferred skills/qualifications
    responsibilities = Column(JSON)
    
    experience = Column(JSON)  # min, preferred, level
    skills = Column(JSON)  # required and preferred skills
    salary = Column(JSON)  # min, max, currency
    benefits = Column(JSON)  # Array of benefits
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
