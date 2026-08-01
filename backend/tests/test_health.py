"""
Health check and root API endpoint unit tests.
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """
    Verify GET / returns expected server status message.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "SkinSense AI Backend Running"}


def test_health_endpoint():
    """
    Verify GET /health returns healthy status status.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
