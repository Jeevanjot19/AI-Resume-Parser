"""
Pydantic schemas for resume API matching exact specification.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


# ============================================================================
# UPLOAD REQUEST/RESPONSE SCHEMAS
# ============================================================================

class UploadOptions(BaseModel):
    """Upload options for resume parsing."""
    extractTechnologies: bool = Field(True, description="Extract technology stack")
    performOCR: bool = Field(True, description="Perform OCR on images")
    enhanceWithAI: bool = Field(True, description="Enhance with AI analysis")
    anonymize: bool = Field(False, description="Anonymize personal information")
    language: str = Field("en", description="Resume language")
    
    class Config:
        schema_extra = {
            "example": {
                "extractTechnologies": True,
                "performOCR": True,
                "enhanceWithAI": True,
                "anonymize": False,
                "language": "en"
            }
        }


class ResumeUploadResponse(BaseModel):
    """Response schema for resume upload."""
    id: str = Field(..., description="Resume UUID")
    status: str = Field(..., description="Processing status")
    message: str = Field(..., description="Status message")
    estimatedProcessingTime: int = Field(..., description="Estimated processing time in seconds")
    webhookUrl: Optional[str] = Field(None, description="Optional callback URL")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "processing",
                "message": "Resume uploaded successfully",
                "estimatedProcessingTime": 30,
                "webhookUrl": None
            }
        }


# ============================================================================
# RESUME RETRIEVAL RESPONSE SCHEMAS
# ============================================================================

class ResumeMetadata(BaseModel):
    """Resume metadata."""
    fileName: str = Field(..., description="Original filename")
    fileSize: int = Field(..., description="File size in bytes")
    uploadedAt: str = Field(..., description="Upload timestamp")
    processedAt: Optional[str] = Field(None, description="Processing completion timestamp")
    processingTime: Optional[float] = Field(None, description="Processing time in seconds")


class NameInfo(BaseModel):
    """Name information."""
    first: Optional[str] = Field(None, description="First name")
    last: Optional[str] = Field(None, description="Last name")
    full: str = Field(..., description="Full name")


class AddressInfo(BaseModel):
    """Address information."""
    street: Optional[str] = Field(None, description="Street address")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State/Province")
    zipCode: Optional[str] = Field(None, description="ZIP/Postal code")
    country: Optional[str] = Field(None, description="Country")


class ContactInfo(BaseModel):
    """Contact information."""
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    address: Optional[AddressInfo] = Field(None, description="Physical address")
    linkedin: Optional[str] = Field(None, description="LinkedIn URL")
    website: Optional[str] = Field(None, description="Personal website URL")
    github: Optional[str] = Field(None, description="GitHub URL")


class PersonalInfo(BaseModel):
    """Personal information."""
    name: NameInfo = Field(..., description="Name information")
    contact: ContactInfo = Field(..., description="Contact information")


class SummaryInfo(BaseModel):
    """Professional summary."""
    text: Optional[str] = Field(None, description="Summary text")
    careerLevel: Optional[str] = Field(None, description="Career level")
    industryFocus: Optional[str] = Field(None, description="Industry focus")


class ExperienceItem(BaseModel):
    """Work experience item."""
    id: str = Field(..., description="Experience ID")
    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    location: Optional[str] = Field(None, description="Job location")
    startDate: Optional[str] = Field(None, description="Start date (ISO format)")
    endDate: Optional[str] = Field(None, description="End date (ISO format)")
    current: bool = Field(False, description="Currently working here")
    duration: Optional[str] = Field(None, description="Human-readable duration")
    description: Optional[str] = Field(None, description="Job description")
    achievements: List[str] = Field(default_factory=list, description="Key achievements")
    technologies: List[str] = Field(default_factory=list, description="Technologies used")


class EducationItem(BaseModel):
    """Education item."""
    degree: Optional[str] = Field(None, description="Degree earned")
    field: Optional[str] = Field(None, description="Field of study")
    institution: str = Field(..., description="Educational institution")
    location: Optional[str] = Field(None, description="Institution location")
    graduationDate: Optional[str] = Field(None, description="Graduation date (ISO format)")
    gpa: Optional[float] = Field(None, description="GPA")
    honors: List[str] = Field(default_factory=list, description="Honors and awards")


class SkillCategory(BaseModel):
    """Skill category."""
    category: str = Field(..., description="Category name")
    items: List[str] = Field(..., description="Skills in this category")


class LanguageSkill(BaseModel):
    """Language proficiency."""
    language: str = Field(..., description="Language name")
    proficiency: str = Field(..., description="Proficiency level")


class SkillsInfo(BaseModel):
    """Skills information."""
    technical: List[SkillCategory] = Field(default_factory=list, description="Technical skills")
    soft: List[str] = Field(default_factory=list, description="Soft skills")
    languages: List[LanguageSkill] = Field(default_factory=list, description="Language proficiencies")


class CertificationItem(BaseModel):
    """Certification item."""
    name: str = Field(..., description="Certification name")
    issuer: str = Field(..., description="Issuing organization")
    issueDate: Optional[str] = Field(None, description="Issue date (ISO format)")
    expiryDate: Optional[str] = Field(None, description="Expiry date (ISO format)")
    credentialId: Optional[str] = Field(None, description="Credential ID")


class AIEnhancements(BaseModel):
    """AI-generated enhancements."""
    qualityScore: int = Field(..., description="Quality score (0-100)")
    completenessScore: int = Field(..., description="Completeness score (0-100)")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")
    industryFit: Dict[str, float] = Field(default_factory=dict, description="Industry fit scores")
    careerProgression: Optional[Dict[str, Any]] = Field(None, description="Career progression analysis")
    skillGaps: Optional[List[str]] = Field(None, description="Identified skill gaps")


class ResumeResponse(BaseModel):
    """Complete resume response."""
    id: str = Field(..., description="Resume UUID")
    metadata: ResumeMetadata = Field(..., description="Resume metadata")
    personalInfo: PersonalInfo = Field(..., description="Personal information")
    summary: SummaryInfo = Field(..., description="Professional summary")
    experience: List[ExperienceItem] = Field(default_factory=list, description="Work experience")
    education: List[EducationItem] = Field(default_factory=list, description="Education")
    skills: SkillsInfo = Field(..., description="Skills")
    certifications: List[CertificationItem] = Field(default_factory=list, description="Certifications")
    aiEnhancements: AIEnhancements = Field(..., description="AI enhancements")


# ============================================================================
# JOB MATCHING REQUEST/RESPONSE SCHEMAS
# ============================================================================

class ExperienceRequirement(BaseModel):
    """Experience requirements."""
    minimum: int = Field(..., description="Minimum years required")
    preferred: int = Field(..., description="Preferred years")
    level: str = Field(..., description="Experience level (entry/mid/senior/executive)")


class Requirements(BaseModel):
    """Job requirements."""
    required: List[str] = Field(default_factory=list, description="Required qualifications")
    preferred: List[str] = Field(default_factory=list, description="Preferred qualifications")


class SkillsRequirement(BaseModel):
    """Skills requirements."""
    required: List[str] = Field(default_factory=list, description="Required skills")
    preferred: List[str] = Field(default_factory=list, description="Preferred skills")


class SalaryRange(BaseModel):
    """Salary range."""
    min: int = Field(..., description="Minimum salary")
    max: int = Field(..., description="Maximum salary")
    currency: str = Field("USD", description="Currency code")


class JobDescription(BaseModel):
    """Job description for matching."""
    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    location: Optional[str] = Field(None, description="Job location")
    type: str = Field(..., description="Job type (full-time, part-time, contract)")
    experience: ExperienceRequirement = Field(..., description="Experience requirements")
    description: str = Field(..., description="Job description text")
    requirements: Requirements = Field(..., description="Job requirements")
    skills: SkillsRequirement = Field(..., description="Required skills")
    salary: Optional[SalaryRange] = Field(None, description="Salary range")
    benefits: List[str] = Field(default_factory=list, description="Benefits offered")
    industry: str = Field(..., description="Industry")


class MatchOptions(BaseModel):
    """Matching options."""
    includeExplanation: bool = Field(True, description="Include detailed explanation")
    detailedBreakdown: bool = Field(True, description="Include detailed score breakdown")
    suggestImprovements: bool = Field(True, description="Suggest improvements")


class JobMatchRequest(BaseModel):
    """Job matching request."""
    jobDescription: JobDescription = Field(..., description="Job description")
    options: MatchOptions = Field(default_factory=MatchOptions, description="Matching options")


class CategoryScoreDetails(BaseModel):
    """Category score details."""
    score: int = Field(..., description="Score (0-100)")
    weight: int = Field(..., description="Weight in overall score")
    details: Dict[str, Any] = Field(..., description="Detailed breakdown")


class CriticalGap(BaseModel):
    """Critical gap item."""
    category: str = Field(..., description="Gap category")
    missing: str = Field(..., description="Missing element")
    impact: str = Field(..., description="Impact level (low/medium/high)")
    suggestion: str = Field(..., description="Improvement suggestion")


class ImprovementArea(BaseModel):
    """Improvement area."""
    category: str = Field(..., description="Category")
    missing: Optional[Any] = Field(None, description="Missing elements (string or list)")
    gap: Optional[str] = Field(None, description="Gap description")
    impact: str = Field(..., description="Impact level")
    suggestion: str = Field(..., description="Improvement suggestion")


class GapAnalysis(BaseModel):
    """Gap analysis."""
    criticalGaps: List[CriticalGap] = Field(default_factory=list, description="Critical gaps")
    improvementAreas: List[ImprovementArea] = Field(default_factory=list, description="Improvement areas")


class SalaryAlignment(BaseModel):
    """Salary alignment."""
    candidateExpectation: str = Field(..., description="Candidate salary expectation")
    jobSalaryRange: str = Field(..., description="Job salary range")
    marketRate: Optional[str] = Field(None, description="Market rate")
    alignment: str = Field(..., description="Alignment status")


class Explanation(BaseModel):
    """Match explanation."""
    summary: str = Field(..., description="Summary text")
    keyFactors: List[str] = Field(default_factory=list, description="Key factors")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")


class MatchMetadata(BaseModel):
    """Matching metadata."""
    matchedAt: str = Field(..., description="Match timestamp")
    processingTime: float = Field(..., description="Processing time in seconds")
    algorithm: str = Field(..., description="Algorithm version")
    confidenceFactors: Dict[str, float] = Field(default_factory=dict, description="Confidence factors")


class MatchingResults(BaseModel):
    """Matching results."""
    overallScore: int = Field(..., description="Overall match score (0-100)")
    confidence: float = Field(..., description="Confidence score (0-1)")
    recommendation: str = Field(..., description="Match recommendation")
    categoryScores: Dict[str, CategoryScoreDetails] = Field(..., description="Category scores")
    strengthAreas: List[str] = Field(default_factory=list, description="Strength areas")
    gapAnalysis: GapAnalysis = Field(..., description="Gap analysis")
    salaryAlignment: SalaryAlignment = Field(..., description="Salary alignment")
    competitiveAdvantages: List[str] = Field(default_factory=list, description="Competitive advantages")


class JobMatchResponse(BaseModel):
    """Job matching response."""
    matchId: str = Field(..., description="Match UUID")
    resumeId: str = Field(..., description="Resume UUID")
    jobTitle: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    matchingResults: MatchingResults = Field(..., description="Matching results")
    explanation: Explanation = Field(..., description="Detailed explanation")
    metadata: MatchMetadata = Field(..., description="Match metadata")


# ============================================================================
# ADDITIONAL SCHEMAS
# ============================================================================

class ProcessingStatusEnum(str, Enum):
    """Processing status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


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


class HealthResponse(BaseModel):
    """Response schema for health check."""
    status: str = Field(..., description="Overall health status")
    timestamp: str = Field(..., description="Health check timestamp")
    version: str = Field(..., description="API version")
    services: Dict[str, Dict[str, Any]] = Field(..., description="Service status")
    environment: Optional[str] = Field(None, description="Environment name")


class ErrorResponse(BaseModel):
    """Response schema for errors."""
    detail: str = Field(..., description="Error message")
    status_code: int = Field(..., description="HTTP status code")
    timestamp: Optional[str] = Field(None, description="Error timestamp")

