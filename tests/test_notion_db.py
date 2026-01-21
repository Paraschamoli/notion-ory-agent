import sys
import os
import asyncio

# Add src to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.notion_service import notion_service

async def test_database():
    print("Testing Notion Database Access...")
    
    # Test 1: Query the database
    print("\n1. Querying database...")
    result = await notion_service.query_database(page_size=5)
    
    if result.get("success"):
        count = result.get("count", 0)
        print(f"✓ Success! Found {count} pages in database")
        
        if count > 0:
            print("Sample pages found:")
            for i, page in enumerate(result.get("results", [])[:3], 1):
                props = page.get("properties", {})
                title = "Untitled"
                
                if "Name" in props and "title" in props["Name"]:
                    titles = props["Name"]["title"]
                    if titles:
                        title = titles[0].get("plain_text", "Untitled")
                
                print(f"  {i}. {title}")
    else:
        print(f"✗ Error: {result.get('error')}")
    
    # Test 2: Create a test page
    print("\n2. Creating a test page...")
    create_result = await notion_service.create_page(
        properties={
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": "Test from Python Agent"
                        }
                    }
                ]
            }
        },
        content="This page was created by the Notion Ory Agent"
    )
    
    if create_result.get("success"):
        print(f"✓ Page created successfully!")
        print(f"  Page ID: {create_result.get('page_id')}")
        print(f"  URL: {create_result.get('url')}")
    else:
        print(f"✗ Error creating page: {create_result.get('error')}")

if __name__ == "__main__":
    asyncio.run(test_database())