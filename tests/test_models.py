import pytest
from sqlalchemy.orm import Session
from app.models.resume import Resume, PersonInfo, WorkExperience, Education, Skill

def test_resume_creation(db: Session):
    """Test resume model creation and relationships"""
    resume = Resume(
        file_name="test.pdf",
        file_size=1024,
        file_type="pdf",
        file_hash="test_hash"
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    
    assert resume.id is not None
    assert resume.created_at is not None
    assert resume.processing_status == "pending"

def test_person_info_relationship(db: Session):
    """Test person info relationship with resume"""
    resume = Resume(
        file_name="test.pdf",
        file_size=1024,
        file_type="pdf",
        file_hash="test_hash_2"
    )
    db.add(resume)
    
    person_info = PersonInfo(
        resume=resume,
        full_name="John Doe",
        email="john@example.com"
    )
    db.add(person_info)
    db.commit()
    
    assert resume.person_info is not None
    assert resume.person_info.full_name == "John Doe"

def test_work_experience_relationship(db: Session):
    """Test work experience relationship with resume"""
    resume = Resume(
        file_name="test.pdf",
        file_size=1024,
        file_type="pdf",
        file_hash="test_hash_3"
    )
    db.add(resume)
    
    experience = WorkExperience(
        resume=resume,
        job_title="Software Engineer",
        company_name="Tech Corp"
    )
    db.add(experience)
    db.commit()
    
    assert len(resume.work_experiences) == 1
    assert resume.work_experiences[0].job_title == "Software Engineer"

def test_education_relationship(db: Session):
    """Test education relationship with resume"""
    resume = Resume(
        file_name="test.pdf",
        file_size=1024,
        file_type="pdf",
        file_hash="test_hash_4"
    )
    db.add(resume)
    
    education = Education(
        resume=resume,
        degree="Bachelor of Science",
        field_of_study="Computer Science"
    )
    db.add(education)
    db.commit()
    
    assert len(resume.education) == 1
    assert resume.education[0].degree == "Bachelor of Science"

def test_skills_relationship(db: Session):
    """Test skills relationship with resume"""
    resume = Resume(
        file_name="test.pdf",
        file_size=1024,
        file_type="pdf",
        file_hash="test_hash_5"
    )
    db.add(resume)
    
    skills = [
        Skill(resume=resume, skill_name="Python", skill_category="Programming"),
        Skill(resume=resume, skill_name="Machine Learning", skill_category="AI")
    ]
    db.add_all(skills)
    db.commit()
    
    assert len(resume.skills) == 2
    skill_names = {skill.skill_name for skill in resume.skills}
    assert "Python" in skill_names
    assert "Machine Learning" in skill_names

def test_cascade_delete(db: Session):
    """Test cascade delete of resume and related entities"""
    resume = Resume(
        file_name="test.pdf",
        file_size=1024,
        file_type="pdf",
        file_hash="test_hash_6"
    )
    db.add(resume)
    
    person_info = PersonInfo(
        resume=resume,
        full_name="John Doe"
    )
    db.add(person_info)
    
    experience = WorkExperience(
        resume=resume,
        job_title="Developer",
        company_name="Tech Corp"
    )
    db.add(experience)
    
    db.commit()
    
    # Delete resume
    db.delete(resume)
    db.commit()
    
    # Verify cascade delete
    assert db.query(PersonInfo).filter_by(resume_id=resume.id).first() is None
    assert db.query(WorkExperience).filter_by(resume_id=resume.id).first() is None