from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ExperienceRequirement(BaseModel):
    minimum: int
    preferred: int
    level: str

class Requirements(BaseModel):
    required: List[str]
    preferred: List[str]

class SalaryRange(BaseModel):
    min: int
    max: int
    currency: str

class JobDescription(BaseModel):
    title: str
    company: str
    location: Optional[str]
    type: str  # full-time, part-time, contract
    experience: ExperienceRequirement
    description: str
    requirements: Requirements
    skills: Requirements
    salary: Optional[SalaryRange]
    benefits: Optional[List[str]]
    industry: str

class CategoryScore(BaseModel):
    score: int
    weight: int
    details: dict

class MatchAnalysis(BaseModel):
    critical_gaps: List[dict]  # List of {category, missing, impact, suggestion}
    improvement_areas: List[dict]

class JobMatchResponse(BaseModel):
    match_id: str
    resume_id: str
    job_title: str
    company: str
    overall_score: int
    confidence: float
    recommendation: str
    category_scores: dict  # Dict of category -> CategoryScore
    gap_analysis: MatchAnalysis
    salary_alignment: dict
    competitive_advantages: List[str]
    explanation: dict
    metadata: dict