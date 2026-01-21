import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.notion_service import notion_service

async def debug_create():
    print("Debugging page creation...")
    
    # Simple test without Status property
    result = await notion_service.create_page(
        properties={
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": "Simple Test Page"
                        }
                    }
                ]
            }
        },
        content="Simple test without complex properties"
    )
    
    print(f"Result: {result}")

if __name__ == "__main__":
    asyncio.run(debug_create())