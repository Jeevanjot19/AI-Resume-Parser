import pytest
from fastapi.testclient import TestClient
import io

@pytest.fixture
def job_description():
    return {
        "title": "Software Engineer",
        "description": "Python developer with FastAPI experience",
        "requirements": ["Python", "FastAPI", "PostgreSQL"],
        "preferred": ["Docker", "AWS"],
        "experience_years": 3
    }

@pytest.fixture
def resume_id():
    return "test-resume-123"

def test_match_resume_success(client, resume_id, job_description):
    """Test successful resume-job matching"""
    response = client.post(
        f"/api/v1/jobs/{resume_id}/match",
        json=job_description
    )
    assert response.status_code == 200
    data = response.json()
    assert "match_score" in data
    assert "skill_matches" in data
    assert "missing_skills" in data
    assert "recommendations" in data

def test_match_resume_invalid_id(client, job_description):
    """Test matching with invalid resume ID"""
    response = client.post(
        "/api/v1/jobs/nonexistent/match",
        json=job_description
    )
    assert response.status_code == 400
    assert "detail" in response.json()

def test_match_resume_invalid_job_data(client, resume_id):
    """Test matching with invalid job data"""
    response = client.post(
        f"/api/v1/jobs/{resume_id}/match",
        json={"invalid": "data"}
    )
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data

def test_match_resume_missing_fields(client, resume_id, job_description):
    """Test matching with missing required fields"""
    del job_description["title"]
    response = client.post(
        f"/api/v1/jobs/{resume_id}/match",
        json=job_description
    )
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data