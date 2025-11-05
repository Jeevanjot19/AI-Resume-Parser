"""
Person Info model.
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, String, ForeignKey, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class PersonInfo(Base):
    """Personal information model."""
    
    __tablename__ = "person_info"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    
    full_name = Column(String(255), index=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(255), index=True)
    phone = Column(String(50))
    address = Column(JSON)  # Full address structure
    social_links = Column(JSON)  # LinkedIn, GitHub, etc.
    
    resume = relationship("Resume", back_populates="person_info")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<PersonInfo(id={self.id}, name={self.full_name})>"

