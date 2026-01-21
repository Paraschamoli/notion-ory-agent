from typing import Optional, Dict, Any, List
import httpx
from src.config import settings

class NotionService:
    """Service for interacting with Notion API."""
    
    def __init__(self):
        self.api_key = settings.notion_api_key
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
    
    async def check_connection(self) -> Dict[str, Any]:
        """Check if connection to Notion API works."""
        if not self.api_key:
            return {
                "status": "error",
                "error": "NOTION_API_KEY not configured"
            }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/users/me",
                    headers=self.headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    user_data = response.json()
                    return {
                        "status": "connected",
                        "user": {
                            "name": user_data.get("name"),
                            "email": user_data.get("person", {}).get("email"),
                            "id": user_data.get("id")
                        },
                        "message": "Successfully connected to Notion API"
                    }
                else:
                    return {
                        "status": "error",
                        "error": f"API Error: {response.status_code}",
                        "details": response.text
                    }
            except Exception as e:
                return {
                    "status": "error",
                    "error": f"Connection failed: {str(e)}"
                }
    
    async def query_database(
        self,
        database_id: Optional[str] = None,
        filter_properties: Optional[List[str]] = None,
        page_size: int = 100
    ) -> Dict[str, Any]:
        """Query a Notion database."""
        db_id = database_id or settings.notion_database_id
        
        if not db_id:
            return {
                "success": False,
                "error": "No database ID provided and NOTION_DATABASE_ID not configured"
            }
        
        payload = {
            "page_size": page_size
        }
        
        if filter_properties:
            payload["filter_properties"] = filter_properties
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/databases/{db_id}/query",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "results": data.get("results", []),
                        "has_more": data.get("has_more", False),
                        "next_cursor": data.get("next_cursor"),
                        "count": len(data.get("results", [])),
                        "database_id": db_id
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to query database: {response.status_code}",
                        "details": response.text,
                        "status_code": response.status_code
                    }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Exception occurred: {str(e)}"
                }
    
    async def create_page(
        self,
        database_id: Optional[str] = None,
        properties: Dict[str, Any] = None,
        content: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new page in a Notion database."""
        db_id = database_id or settings.notion_database_id
        
        if not db_id:
            return {
                "success": False,
                "error": "No database ID provided and NOTION_DATABASE_ID not configured"
            }
        
        # Build the page properties
        page_properties = properties or {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": "New Page"
                        }
                    }
                ]
            }
        }
        
        payload = {
            "parent": {"database_id": db_id},
            "properties": page_properties
        }
        
        # Add content if provided
        if content:
            payload["children"] = [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": content
                                }
                            }
                        ]
                    }
                }
            ]
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/pages",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    page_data = response.json()
                    return {
                        "success": True,
                        "page": page_data,
                        "page_id": page_data.get("id"),
                        "url": page_data.get("url"),
                        "message": "Page created successfully"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to create page: {response.status_code}",
                        "details": response.text,
                        "status_code": response.status_code
                    }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Exception occurred: {str(e)}"
                }
    
    async def get_page(self, page_id: str) -> Dict[str, Any]:
        """Get a Notion page by ID."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/pages/{page_id}",
                    headers=self.headers,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return {
                        "success": True,
                        "page": response.json()
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to get page: {response.status_code}",
                        "details": response.text,
                        "status_code": response.status_code
                    }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Exception occurred: {str(e)}"
                }
    
    async def update_page(
        self,
        page_id: str,
        properties: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update a Notion page."""
        payload = {
            "properties": properties
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.patch(
                    f"{self.base_url}/pages/{page_id}",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return {
                        "success": True,
                        "page": response.json(),
                        "message": "Page updated successfully"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to update page: {response.status_code}",
                        "details": response.text,
                        "status_code": response.status_code
                    }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Exception occurred: {str(e)}"
                }
    
    async def search(
        self,
        query: str = "",
        filter_type: str = "page",  # "page" or "database"
        page_size: int = 20
    ) -> Dict[str, Any]:
        """Search in Notion."""
        payload = {
            "query": query,
            "page_size": page_size,
            "filter": {
                "value": filter_type,
                "property": "object"
            }
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/search",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "results": data.get("results", []),
                        "has_more": data.get("has_more", False),
                        "next_cursor": data.get("next_cursor"),
                        "count": len(data.get("results", []))
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to search: {response.status_code}",
                        "details": response.text,
                        "status_code": response.status_code
                    }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Exception occurred: {str(e)}"
                }

# Singleton instance
notion_service = NotionService()