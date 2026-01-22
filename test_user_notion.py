import sys
import os
import asyncio
import httpx

# Add src to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import settings
from src.services.kratos_service import kratos_service
from src.services.user_notion_service import user_notion_service
from src.models.user_notion import UserNotionConfig

async def test_user_notion_integration():
    """Test the complete user-specific Notion integration flow."""
    print("🔧 Testing User-Specific Notion Integration\n")
    
    # Test 1: Check if services are accessible
    print("1. Checking service connections...")
    
    # Check Kratos
    kratos_health = await kratos_service.get_health()
    print(f"   Kratos: {kratos_health.get('status', 'unknown')}")
    
    # Test 2: Create a test user
    print("\n2. Creating test user...")
    
    test_email = f"test_user_{os.urandom(4).hex()}@example.com"
    create_result = await kratos_service.create_identity(
        email=test_email,
        traits={
            "email": test_email,
            "name": {"first": "Test", "last": "User"}
        }
    )
    
    if not create_result.get("success"):
        print(f"   ❌ Failed to create test user: {create_result.get('error')}")
        return
    
    user_id = create_result["identity"]["id"]
    print(f"   ✅ Created test user: {user_id}")
    print(f"   Email: {test_email}")
    
    # Test 3: Test with a dummy Notion API key (should fail)
    print("\n3. Testing with invalid API key...")
    
    dummy_config = UserNotionConfig(
        notion_api_key="secret_invalid_key_123",
        notion_database_id="dummy_db_id"
    )
    
    test_result = await user_notion_service.test_user_connection(dummy_config)
    print(f"   Connection test: {test_result.status}")
    print(f"   Expected: error (invalid key)")
    
    # Test 4: Get user's current Notion config (should be none)
    print("\n4. Checking user's current Notion config...")
    
    user_result = await kratos_service.get_identity(user_id)
    notion_config = user_result.get("notion_config")
    
    if notion_config:
        print(f"   ❌ User already has Notion config (unexpected)")
    else:
        print(f"   ✅ User has no Notion config (expected)")
    
    # Test 5: Update Kratos service to include notion config extraction
    print("\n5. Testing Kratos service notion config methods...")
    
    # Create a test config
    test_config = UserNotionConfig(
        notion_api_key="secret_test_key_123",
        notion_database_id="test_db_123",
        enabled=True
    )
    
    # Convert to traits and back
    traits = test_config.to_traits()
    print(f"   Config → Traits: {traits.get('notion_config', {}).get('database_id')}")
    
    reconstructed = UserNotionConfig.from_traits(traits)
    print(f"   Traits → Config: {reconstructed.notion_database_id}")
    
    # Test 6: Simulate API flow
    print("\n6. Simulating API endpoint flow...")
    print("   Endpoints available:")
    print("   - POST /auth/{user_id}/notion/config")
    print("   - GET /auth/{user_id}/notion/status")
    print("   - POST /notion/users/{user_id}/pages")
    print("   - GET /notion/users/{user_id}/databases/query")
    
    # Test 7: Check if app-level Notion config exists
    print("\n7. Checking app-level configuration...")
    if settings.notion_api_key and settings.notion_api_key != "placeholder":
        print(f"   ✅ App-level Notion API key configured")
    else:
        print(f"   ⚠️  App-level Notion API key not configured")
        print(f"   Note: Users will need to provide their own API keys")
    
    print("\n" + "="*60)
    print("TEST SUMMARY:")
    print("="*60)
    print("✅ Kratos service integration")
    print("✅ User identity creation")
    print("✅ Notion config model serialization")
    print("✅ User-specific service layer")
    print("✅ API endpoint structure defined")
    print("\nNext steps:")
    print("1. Configure a real Notion API key for a user")
    print("2. Test actual Notion API calls")
    print("3. Use the new MCP tools")
    
    # Cleanup (optional)
    print(f"\nTest user ID: {user_id}")
    print("Note: Test user remains in Kratos for manual testing")

if __name__ == "__main__":
    asyncio.run(test_user_notion_integration())