import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    print("✓ Root endpoint works")

def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    print("✓ Health check works")

def test_readiness():
    """Test readiness endpoint."""
    response = client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    print("✓ Readiness check works")

def test_liveness():
    """Test liveness endpoint."""
    response = client.get("/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"
    print("✓ Liveness check works")

if __name__ == "__main__":
    # Run all tests
    test_root_endpoint()
    test_health_check()
    test_readiness()
    test_liveness()
    print("\n✅ All API tests passed!")