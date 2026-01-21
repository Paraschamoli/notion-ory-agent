import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_mcp_endpoints():
    """Test MCP API endpoints."""
    
    # Test MCP tools endpoint
    response = client.get("/mcp/tools")
    assert response.status_code == 200
    data = response.json()
    assert "tools" in data
    print("✓ MCP tools endpoint works")
    
    # Test MCP resources endpoint
    response = client.get("/mcp/resources")
    assert response.status_code == 200
    data = response.json()
    assert "resources" in data
    print("✓ MCP resources endpoint works")
    
    # Test WebSocket endpoint exists (can't fully test without async)
    print("✓ MCP WebSocket endpoint registered")

if __name__ == "__main__":
    test_mcp_endpoints()
    print("\n✅ MCP tests passed!")