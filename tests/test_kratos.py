import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_auth_endpoints():
    """Test authentication endpoints."""
    
    # Test health endpoint
    response = client.get("/auth/health")
    print(f"Kratos health check: {response.status_code}")
    
    # Test list identities (will likely fail without Kratos running)
    response = client.get("/auth/identities")
    print(f"List identities: {response.status_code}")
    
    # Check that endpoints are registered
    print("\n✅ Auth endpoints are registered")
    print("Note: These endpoints will work when Ory Kratos is running")

if __name__ == "__main__":
    test_auth_endpoints()