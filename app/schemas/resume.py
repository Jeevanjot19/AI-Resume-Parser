"""
Pydantic schemas for resume API.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


# Enums
class ProcessingStatusEnum(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


# Request schemas
class JobMatchRequest(BaseModel):
    """Request schema for job matching."""
    id: Optional[str] = None
    title: str = Field(..., description="Job title")
    description: Optional[str] = Field(None, description="Job description")
    requirements: Optional[List[str]] = Field(None, description="Job requirements")
    responsibilities: Optional[List[str]] = Field(None, description="Job responsibilities")
    required_experience_years: Optional[int] = Field(0, description="Required years of experience")
    required_degree: Optional[str] = Field(None, description="Required education degree")
    industry: Optional[str] = Field(None, description="Industry")
    level: Optional[str] = Field(None, description="Career level")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "job-123",
                "title": "Senior Software Engineer",
                "description": "We are looking for an experienced software engineer...",
                "requirements": ["Python", "FastAPI", "Docker", "AWS"],
                "responsibilities": ["Design and implement features", "Code review"],
                "required_experience_years": 5,
                "required_degree": "Bachelor's in Computer Science",
                "industry": "Software Engineering",
                "level": "Senior"
            }
        }


# Response schemas
class ResumeUploadResponse(BaseModel):
    """Response schema for resume upload."""
    id: str = Field(..., description="Resume UUID")
    filename: str = Field(..., description="Original filename")
    status: str = Field(..., description="Processing status")
    message: str = Field(..., description="Status message")
    uploaded_at: str = Field(..., description="Upload timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "filename": "john_doe_resume.pdf",
                "status": "PENDING",
                "message": "Resume uploaded successfully. Processing started.",
                "uploaded_at": "2024-01-15T10:30:00Z"
            }
        }


class ResumeResponse(BaseModel):
    """Response schema for resume data."""
    id: str = Field(..., description="Resume UUID")
    filename: str = Field(..., description="Original filename")
    file_type: str = Field(..., description="File type")
    processing_status: str = Field(..., description="Processing status")
    raw_text: Optional[str] = Field(None, description="Extracted text")
    structured_data: Optional[Dict[str, Any]] = Field(None, description="Parsed structured data")
    ai_enhancements: Optional[Dict[str, Any]] = Field(None, description="AI enhancements")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "filename": "john_doe_resume.pdf",
                "file_type": "pdf",
                "processing_status": "COMPLETED",
                "structured_data": {
                    "personal_info": {
                        "full_name": "John Doe",
                        "email": "john@example.com",
                        "phone": "+1234567890"
                    },
                    "skills": ["Python", "FastAPI", "Docker"],
                    "total_experience_years": 5
                },
                "ai_enhancements": {
                    "quality_score": 85.5,
                    "industry_fit": {"top_industry": "Software Engineering"}
                },
                "created_at": "2024-01-15T10:30:00Z"
            }
        }


class ResumeAnalysis(BaseModel):
    """Response schema for resume AI analysis."""
    resume_id: str = Field(..., description="Resume UUID")
    quality_score: float = Field(..., description="Overall quality score (0-100)")
    completeness_score: float = Field(..., description="Completeness score (0-100)")
    industry_matches: Dict[str, Any] = Field(..., description="Industry fit analysis")
    skill_gaps: List[str] = Field(..., description="Identified skill gaps")
    improvement_suggestions: List[str] = Field(..., description="Improvement suggestions")
    career_path_analysis: Dict[str, Any] = Field(..., description="Career path analysis")
    ai_enhancements: Optional[Dict[str, Any]] = Field(None, description="Full AI enhancements")
    analyzed_at: str = Field(..., description="Analysis timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "resume_id": "550e8400-e29b-41d4-a716-446655440000",
                "quality_score": 85.5,
                "completeness_score": 90.0,
                "industry_matches": {
                    "top_industry": "Software Engineering",
                    "confidence": 0.92
                },
                "skill_gaps": ["Kubernetes", "AWS Lambda"],
                "improvement_suggestions": [
                    "Add more quantifiable achievements",
                    "Include relevant certifications"
                ],
                "career_path_analysis": {
                    "current_level": "Mid-level",
                    "next_steps": ["Senior", "Lead"]
                },
                "analyzed_at": "2024-01-15T10:35:00Z"
            }
        }


class JobMatchResponse(BaseModel):
    """Response schema for job matching."""
    resume_id: str = Field(..., description="Resume UUID")
    job_title: str = Field(..., description="Job title")
    overall_score: float = Field(..., description="Overall match score (0-100)")
    category_scores: Dict[str, Any] = Field(..., description="Breakdown of scores by category")
    gap_analysis: Dict[str, Any] = Field(..., description="Gap analysis")
    recommendations: List[str] = Field(..., description="Recommendations")
    matched_at: str = Field(..., description="Match timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "resume_id": "550e8400-e29b-41d4-a716-446655440000",
                "job_title": "Senior Software Engineer",
                "overall_score": 87.5,
                "category_scores": {
                    "semantic_similarity": 88.0,
                    "skills": {
                        "score": 85.0,
                        "matched_skills": ["Python", "Docker"],
                        "missing_skills": ["Kubernetes"]
                    },
                    "experience": {
                        "score": 90.0,
                        "years_match": True
                    }
                },
                "gap_analysis": {
                    "critical_gaps": ["Missing required skill: Kubernetes"],
                    "strengths": ["Meets experience requirement (5 years)"]
                },
                "recommendations": [
                    "Strong match! Consider applying for this position",
                    "Consider acquiring Kubernetes certification"
                ],
                "matched_at": "2024-01-15T10:40:00Z"
            }
        }


class HealthResponse(BaseModel):
    """Response schema for health check."""
    status: str = Field(..., description="Overall health status")
    timestamp: str = Field(..., description="Health check timestamp")
    version: str = Field(..., description="API version")
    services: Dict[str, Dict[str, Any]] = Field(..., description="Service status")
    environment: Optional[str] = Field(None, description="Environment name")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2024-01-15T10:30:00Z",
                "version": "1.0.0",
                "services": {
                    "api": {"status": "up", "healthy": True},
                    "database": {"status": "up", "healthy": True},
                    "redis": {"status": "up", "healthy": True},
                    "elasticsearch": {"status": "up", "healthy": True},
                    "tika": {"status": "up", "healthy": True}
                },
                "environment": "production"
            }
        }


class ErrorResponse(BaseModel):
    """Response schema for errors."""
    detail: str = Field(..., description="Error message")
    status_code: int = Field(..., description="HTTP status code")
    timestamp: Optional[str] = Field(None, description="Error timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "detail": "Resume not found",
                "status_code": 404,
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }
