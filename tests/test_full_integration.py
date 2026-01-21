import sys
import os
import asyncio

# Add src to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.notion_service import notion_service
from src.services.kratos_service import kratos_service
from src.services.hydra_service import hydra_service

async def test_all_services():
    print("=== COMPREHENSIVE INTEGRATION TEST ===\n")
    
    # Test 1: Notion Service
    print("1. Testing Notion Service...")
    notion_health = await notion_service.check_connection()
    if notion_health.get("status") == "connected":
        print(f"   ✓ Notion: Connected as {notion_health.get('user', {}).get('name')}")
    else:
        print(f"   ✗ Notion: {notion_health.get('error')}")
    
    # Test 2: Kratos Service
    print("\n2. Testing Kratos Service...")
    kratos_health = await kratos_service.get_health()
    print(f"   Kratos Status: {kratos_health.get('status', 'Not running')}")
    
    # Test 3: Hydra Service
    print("\n3. Testing Hydra Service...")
    hydra_health = await hydra_service.get_health()
    print(f"   Hydra Status: {hydra_health.get('status', 'Not running')}")
    
    # Test 4: Create a sample Notion page
    print("\n4. Testing Notion Page Creation...")
    create_result = await notion_service.create_page(
        properties={
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": "Final Integration Test"
                        }
                    }
                ]
            }
        },
        content="This page was created during the final integration test of the Notion Ory Agent."
    )
    
    if create_result.get("success"):
        print(f"   ✓ Page created: {create_result.get('url')}")
    else:
        print(f"   ✗ Error: {create_result.get('error')}")
    
    print("\n=== TEST COMPLETE ===")

if __name__ == "__main__":
    asyncio.run(test_all_services())