"""
Work Experience model.
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class WorkExperience(Base):
    """Work experience model."""
    
    __tablename__ = "work_experience"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    
    job_title = Column(String(255), nullable=False, index=True)
    company_name = Column(String(255), nullable=False, index=True)
    location = Column(String(255))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    is_current = Column(Boolean, default=False)
    description = Column(Text)
    achievements = Column(ARRAY(Text))  # Array of achievement strings
    technologies = Column(ARRAY(String))  # Array of technology names
    
    resume = relationship("Resume", back_populates="work_experiences")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<WorkExperience(id={self.id}, title={self.job_title}, company={self.company_name})>"
