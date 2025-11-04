from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class ContactInfo(BaseModel):
    email: EmailStr
    phone: str
    address: dict
    linkedin: Optional[str] = None
    website: Optional[str] = None

class PersonalInfo(BaseModel):
    first_name: str
    last_name: str
    full_name: str
    contact: ContactInfo

class Experience(BaseModel):
    title: str
    company: str
    location: Optional[str]
    start_date: datetime
    end_date: Optional[datetime]
    current: bool
    description: Optional[str]
    achievements: List[str]
    technologies: List[str]

class Education(BaseModel):
    degree: str
    field: str
    institution: str
    location: Optional[str]
    graduation_date: datetime
    gpa: Optional[float]
    honors: Optional[List[str]]

class Skills(BaseModel):
    technical: List[dict]  # List of {category: str, items: List[str]}
    soft: List[str]
    languages: List[dict]  # List of {language: str, proficiency: str}

class Certification(BaseModel):
    name: str
    issuer: str
    issue_date: datetime
    expiry_date: Optional[datetime]
    credential_id: Optional[str]

class IndustryFit(BaseModel):
    software_engineering: float
    data_science: float
    product_management: float

class AIEnhancements(BaseModel):
    quality_score: float
    completeness_score: float
    suggestions: List[str]
    industry_fit: IndustryFit

class ResumeResponse(BaseModel):
    id: str
    metadata: dict
    personal_info: PersonalInfo
    summary: Optional[str]
    experience: List[Experience]
    education: List[Education]
    skills: Skills
    certifications: Optional[List[Certification]]
    ai_enhancements: AIEnhancements

class ResumeAnalysis(BaseModel):
    resume_id: str
    quality_score: int
    completeness_score: int
    industry_matches: List[dict]
    skill_gaps: List[str]
    recommendations: List[str]
    career_path_analysis: dict