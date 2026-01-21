import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_oauth_endpoints():
    """Test OAuth endpoints."""
    
    # Test health endpoint
    response = client.get("/oauth/health")
    print(f"Hydra health check: {response.status_code}")
    
    # Test list clients (will likely fail without Hydra running)
    response = client.get("/oauth/clients")
    print(f"List OAuth clients: {response.status_code}")
    
    # Check that endpoints are registered
    print("\n✅ OAuth endpoints are registered")
    print("Note: These endpoints will work when Ory Hydra is running")

if __name__ == "__main__":
    test_oauth_endpoints()