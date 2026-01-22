from typing import Optional, Dict, Any, List
import httpx
from datetime import datetime
from src.config import settings
from src.models.user_notion import UserNotionConfig, NotionConnectionTest

class UserNotionService:
    """Service for user-specific Notion API operations."""
    
    def __init__(self):
        self.base_url = "https://api.notion.com/v1"
        # App-level fallback configuration
        self.app_api_key = settings.notion_api_key
        self.app_database_id = settings.notion_database_id
    
    def _get_headers(self, api_key: str) -> Dict[str, str]:
        """Get HTTP headers for Notion API."""
        if not api_key:
            raise ValueError("No Notion API key provided")
            
        return {
            "Authorization": f"Bearer {api_key}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
    
    async def test_user_connection(
        self, 
        user_notion_config: UserNotionConfig
    ) -> NotionConnectionTest:
        """Test if a user's Notion API key works."""
        headers = self._get_headers(user_notion_config.notion_api_key.get_secret_value())
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/users/me",
                    headers=headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    user_data = response.json()
                    return NotionConnectionTest(
                        status="connected",
                        user_id=user_data.get("id"),
                        user_name=user_data.get("name"),
                        workspace_name=user_data.get("bot", {}).get("workspace_name"),
                        tested_at=datetime.now()
                    )
                else:
                    return NotionConnectionTest(
                        status="error",
                        error=f"API Error: {response.status_code} - {response.text}",
                        tested_at=datetime.now()
                    )
            except Exception as e:
                return NotionConnectionTest(
                    status="error",
                    error=f"Connection failed: {str(e)}",
                    tested_at=datetime.now()
                )
    
    async def query_user_database(
        self,
        user_notion_config: UserNotionConfig,
        database_id: Optional[str] = None,
        page_size: int = 100
    ) -> Dict[str, Any]:
        """Query a user's Notion database."""
        db_id = database_id or user_notion_config.notion_database_id
        
        if not db_id:
            return {
                "success": False,
                "error": "No database ID provided"
            }
        
        headers = self._get_headers(user_notion_config.notion_api_key.get_secret_value())
        payload = {"page_size": page_size}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/databases/{db_id}/query",
                    headers=headers,
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
                        "database_id": db_id,
                        "user_owned": True
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to query database: {response.status_code}",
                        "details": response.text,
                        "status_code": response.status_code,
                        "user_owned": True
                    }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Exception occurred: {str(e)}",
                    "user_owned": True
                }
    
    async def create_user_page(
        self,
        user_notion_config: UserNotionConfig,
        database_id: Optional[str] = None,
        title: str = "New Page",
        content: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a page in user's Notion database."""
        db_id = database_id or user_notion_config.notion_database_id
        
        if not db_id:
            return {
                "success": False,
                "error": "No database ID provided"
            }
        
        headers = self._get_headers(user_notion_config.notion_api_key.get_secret_value())
        
        payload = {
            "parent": {"database_id": db_id},
            "properties": {
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": title
                            }
                        }
                    ]
                }
            }
        }
        
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
                    headers=headers,
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
                        "message": "Page created successfully",
                        "user_owned": True
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to create page: {response.status_code}",
                        "details": response.text,
                        "status_code": response.status_code,
                        "user_owned": True
                    }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Exception occurred: {str(e)}",
                    "user_owned": True
                }

# Singleton instance
user_notion_service = UserNotionService()