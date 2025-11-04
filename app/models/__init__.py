"""
Database models initialization.
"""

from app.models.resume import Resume, ProcessingStatus
from app.models.person_info import PersonInfo
from app.models.work_experience import WorkExperience
from app.models.education import Education
from app.models.skills import Skill
from app.models.ai_analysis import AIAnalysis
from app.models.resume_job_match import ResumeJobMatch

# Import job model if it exists
try:
    from app.models.job import Job
    __all__ = [
        "Resume",
        "ProcessingStatus",
        "PersonInfo",
        "WorkExperience",
        "Education",
        "Skill",
        "AIAnalysis",
        "ResumeJobMatch",
        "Job",
    ]
except ImportError:
    __all__ = [
        "Resume",
        "ProcessingStatus",
        "PersonInfo",
        "WorkExperience",
        "Education",
        "Skill",
        "AIAnalysis",
        "ResumeJobMatch",
    ]
