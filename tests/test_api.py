import pytest
from fastapi.testclient import TestClient

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "services" in data

def test_invalid_endpoint(client):
    """Test accessing invalid endpoint"""
    response = client.get("/api/v1/nonexistent")
    assert response.status_code == 404