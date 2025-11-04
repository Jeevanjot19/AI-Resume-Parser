"""
Resume and related models for the application.
"""

import uuid
import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, Boolean, Numeric, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
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
    structured_data = Column(JSONB, nullable=True)
    ai_enhancements = Column(JSONB, nullable=True)
    metadata = Column(JSONB, nullable=True)
    
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


class PersonInfo(Base):
    """Personal information model."""
    
    __tablename__ = "person_info"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    
    full_name = Column(String(255), index=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(255), index=True)
    phone = Column(String(50))
    address = Column(JSONB)  # Full address structure
    social_links = Column(JSONB)  # LinkedIn, GitHub, etc.
    
    resume = relationship("Resume", back_populates="person_info")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<PersonInfo(id={self.id}, name={self.full_name})>"


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
    honors = Column(ARRAY(String))  # Array of honors/awards
    
    resume = relationship("Resume", back_populates="education")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Education(id={self.id}, degree={self.degree}, institution={self.institution})>"


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
    created_at = Column(DateTime, default=datetime.utcnow)