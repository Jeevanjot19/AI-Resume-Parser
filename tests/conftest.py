import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base_class import Base
from app.db.session import get_db

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db():
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def client():
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
            
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="module")
def test_pdf():
    """Sample PDF resume content"""
    return b"%PDF-1.4\n...sample PDF content..."

@pytest.fixture(scope="module")
def test_docx():
    """Sample DOCX resume content"""
    return b"PK\x03\x04...sample DOCX content..."

@pytest.fixture(scope="module")
def test_resume_data():
    """Sample resume data"""
    return {
        "personalInfo": {
            "name": {
                "first": "John",
                "last": "Doe",
                "full": "John Doe"
            },
            "contact": {
                "email": "john.doe@example.com",
                "phone": "+1-555-123-4567",
                "address": {
                    "city": "San Francisco",
                    "state": "CA",
                    "country": "USA"
                }
            }
        },
        "experience": [
            {
                "title": "Senior Software Engineer",
                "company": "Tech Corp",
                "startDate": "2021-03-01",
                "endDate": "2025-09-01",
                "current": True
            }
        ],
        "education": [
            {
                "degree": "Bachelor of Science",
                "field": "Computer Science",
                "institution": "University of California",
                "graduationDate": "2018-05-15"
            }
        ],
        "skills": [
            "Python",
            "JavaScript",
            "Machine Learning"
        ]
    }

@pytest.fixture(scope="module")
def test_job_description():
    """Sample job description"""
    return {
        "title": "Senior Software Engineer",
        "company": "Tech Innovation Corp",
        "experience": {
            "minimum": 5,
            "preferred": 8,
            "level": "senior"
        },
        "requirements": {
            "required": [
                "Python",
                "JavaScript",
                "AWS"
            ],
            "preferred": [
                "Machine Learning",
                "Docker"
            ]
        }
    }