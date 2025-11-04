import pytest
from fastapi.testclient import TestClient
import io

@pytest.fixture
def sample_pdf():
    content = b"%PDF-1.4\nTest Resume"
    return io.BytesIO(content)

@pytest.fixture
def resume_id():
    return "test-resume-123"

def test_upload_resume_success(client):
    """Test successful resume upload"""
    files = {"file": ("test.pdf", io.BytesIO(b"%PDF-1.4\nTest Resume"), "application/pdf")}
    response = client.post("/api/v1/resumes/upload", files=files)
    assert response.status_code == 200
    data = response.json()
    assert "text" in data
    assert "extracted" in data

def test_upload_resume_invalid_file(client):
    """Test uploading invalid file type"""
    files = {"file": ("test.invalid", io.BytesIO(b"Invalid content"), "application/octet-stream")}
    response = client.post("/api/v1/resumes/upload", files=files)
    assert response.status_code == 400
    assert "detail" in response.json()

def test_upload_resume_empty_file(client):
    """Test uploading empty file"""
    files = {"file": ("test.pdf", io.BytesIO(b""), "application/pdf")}
    response = client.post("/api/v1/resumes/upload", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == ""

def test_get_resume_success(client, resume_id):
    """Test getting resume by ID"""
    response = client.get(f"/api/v1/resumes/{resume_id}")
    assert response.status_code == 200
    data = response.json()
    assert "text" in data
    assert "extracted" in data

def test_get_resume_not_found(client):
    """Test getting non-existent resume"""
    response = client.get("/api/v1/resumes/nonexistent")
    assert response.status_code == 404
    assert "detail" in response.json()

def test_get_resume_analysis_success(client, resume_id):
    """Test getting resume analysis"""
    response = client.get(f"/api/v1/resumes/{resume_id}/analysis")
    assert response.status_code == 200
    data = response.json()
    assert "quality_score" in data
    assert "improvement_suggestions" in data

def test_get_resume_analysis_not_found(client):
    """Test getting analysis for non-existent resume"""
    response = client.get("/api/v1/resumes/nonexistent/analysis")
    assert response.status_code == 404
    assert "detail" in response.json()

def test_upload_resume_corrupted_file(client):
    """Test uploading corrupted PDF file"""
    files = {"file": ("test.pdf", io.BytesIO(b"%PDF-1.4\nCorrupted content"), "application/pdf")}
    response = client.post("/api/v1/resumes/upload", files=files)
    assert response.status_code == 400
    assert "detail" in response.json()