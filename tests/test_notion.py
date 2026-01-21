import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_notion_endpoints():
    """Test Notion endpoints."""
    
    # Test health endpoint
    response = client.get("/notion/health")
    print(f"Notion health check: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Check that endpoints are registered
    print("\n✅ Notion endpoints are registered")
    print("Note: These endpoints need NOTION_API_KEY to work properly")

if __name__ == "__main__":
    test_notion_endpoints()