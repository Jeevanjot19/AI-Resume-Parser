"""
AI Analysis model for storing AI-generated insights.
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, CheckConstraint, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class AIAnalysis(Base):
    """AI analysis results model."""
    
    __tablename__ = "ai_analysis"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("resumes.id", ondelete="CASCADE"), 
        nullable=False, 
        unique=True,
        index=True
    )
    
    # Quality scores
    quality_score = Column(
        Integer, 
        CheckConstraint("quality_score >= 0 AND quality_score <= 100"),
        nullable=True
    )
    completeness_score = Column(
        Integer,
        CheckConstraint("completeness_score >= 0 AND completeness_score <= 100"),
        nullable=True
    )
    
    # Classifications
    industry_classifications = Column(JSON, nullable=True)  # {"tech": 0.95, "finance": 0.45}
    career_level = Column(String(50), nullable=True)  # entry, mid, senior, executive
    
    # Insights
    salary_estimate = Column(JSON, nullable=True)  # {"min": 80000, "max": 120000, "currency": "USD"}
    suggestions = Column(JSON, nullable=True)  # Improvement suggestions
    confidence_scores = Column(JSON, nullable=True)  # Various confidence metrics
    
    # Additional metadata
    analysis_version = Column(String(50), default="1.0.0")
    processing_time = Column(Integer, nullable=True)  # milliseconds
    
    # Relationships
    resume = relationship("Resume", back_populates="ai_analysis")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<AIAnalysis(id={self.id}, quality={self.quality_score}, career_level={self.career_level})>"

