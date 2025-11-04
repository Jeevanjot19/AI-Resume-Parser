"""
Resume-Job matching model for storing match results.
"""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Numeric, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class ResumeJobMatch(Base):
    """Resume-job matching results model."""
    
    __tablename__ = "resume_job_matches"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(
        UUID(as_uuid=True),
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Job information
    job_title = Column(String(255), nullable=False, index=True)
    company_name = Column(String(255), nullable=True)
    job_description = Column(Text, nullable=False)
    job_requirements = Column(JSONB, nullable=True)  # Structured job requirements
    
    # Match scores
    overall_score = Column(
        Integer,
        CheckConstraint("overall_score >= 0 AND overall_score <= 100"),
        nullable=False,
        index=True
    )
    confidence_score = Column(
        Numeric(3, 2),
        CheckConstraint("confidence_score >= 0 AND confidence_score <= 1"),
        nullable=False
    )
    recommendation = Column(String(50), nullable=True)  # e.g., "Strong Match", "Good Match"
    
    # Detailed breakdown
    category_scores = Column(JSONB, nullable=True)  # Skills, experience, education scores
    strength_areas = Column(ARRAY(Text), nullable=True)  # Candidate's strengths
    gap_analysis = Column(JSONB, nullable=True)  # Missing skills, experience gaps
    salary_alignment = Column(JSONB, nullable=True)  # Salary range comparison
    competitive_advantages = Column(ARRAY(Text), nullable=True)  # Unique selling points
    
    # AI explanation
    explanation = Column(JSONB, nullable=True)  # Detailed match explanation
    processing_metadata = Column(JSONB, nullable=True)  # Algorithm version, processing time, etc.
    
    # Relationships
    resume = relationship("Resume", back_populates="job_matches")
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<ResumeJobMatch(id={self.id}, job={self.job_title}, score={self.overall_score})>"
