"""
Skills model.
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Skill(Base):
    """Skill model."""
    
    __tablename__ = "skills"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    
    skill_name = Column(String(255), nullable=False, index=True)
    skill_category = Column(String(100), index=True)  # e.g., "Programming", "Framework", "Tool"
    proficiency_level = Column(String(50))  # e.g., "Expert", "Intermediate", "Beginner"
    years_of_experience = Column(Integer)
    is_primary = Column(Boolean, default=False)
    
    resume = relationship("Resume", back_populates="skills")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Skill(id={self.id}, name={self.skill_name}, category={self.skill_category})>"
