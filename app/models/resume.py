"""
Resume and related models for the application.
"""

import uuid
import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, Boolean, Numeric, Enum as SQLEnum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class ProcessingStatus(str, enum.Enum):
    """Processing status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Resume(Base):
    """Resume document model."""
    
    __tablename__ = "resumes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(50), nullable=False)
    file_hash = Column(String(128), unique=True, nullable=False, index=True)
    
    # Processing info
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    processed_at = Column(DateTime, nullable=True)
    processing_status = Column(
        SQLEnum(ProcessingStatus),
        default=ProcessingStatus.PENDING,
        nullable=False,
        index=True
    )
    
    # Content
    raw_text = Column(Text, nullable=True)
    structured_data = Column(JSON, nullable=True)
    ai_enhancements = Column(JSON, nullable=True)
    file_metadata = Column(JSON, nullable=True)  # Renamed from 'metadata' to avoid SQLAlchemy reserved word
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    person_info = relationship("PersonInfo", back_populates="resume", uselist=False, cascade="all, delete-orphan")
    work_experiences = relationship("WorkExperience", back_populates="resume", cascade="all, delete-orphan")
    education = relationship("Education", back_populates="resume", cascade="all, delete-orphan")
    skills = relationship("Skill", back_populates="resume", cascade="all, delete-orphan")
    ai_analysis = relationship("AIAnalysis", back_populates="resume", uselist=False, cascade="all, delete-orphan")
    job_matches = relationship("ResumeJobMatch", back_populates="resume", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Resume(id={self.id}, file_name={self.file_name}, status={self.processing_status})>"

