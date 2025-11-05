"""
Education model.
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, String, ForeignKey, DateTime, Numeric, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Education(Base):
    """Education model."""
    
    __tablename__ = "education"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    
    degree = Column(String(255))
    field_of_study = Column(String(255), index=True)
    institution = Column(String(255), index=True)
    location = Column(String(255))
    graduation_date = Column(DateTime)
    gpa = Column(Numeric(3, 2))  # e.g., 3.75
    honors = Column(JSON)  # Array of honors/awards
    
    resume = relationship("Resume", back_populates="education")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Education(id={self.id}, degree={self.degree}, institution={self.institution})>"

