import httpx
from typing import Optional, Dict, Any
from src.config import settings
from src.models.user_notion import UserNotionConfig

class KratosService:
    """Service for interacting with Ory Kratos."""
    
    def __init__(self):
        self.base_url = settings.ory_kratos_url
        self.admin_url = settings.ory_kratos_admin_url or self.base_url.replace("4433", "4434")
        
    async def get_health(self) -> Dict[str, Any]:
        """Check Kratos health status."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.admin_url}/health/ready")
                return {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "status_code": response.status_code,
                    "response": response.json() if response.status_code == 200 else None
                }
            except Exception as e:
                return {
                    "status": "error",
                    "error": str(e)
                }
    
    async def create_identity(self, email: str, traits: Optional[Dict] = None) -> Dict[str, Any]:
        """Create a new identity in Kratos with optional Notion config."""
        payload = {
            "schema_id": "default",
            "traits": traits or {
                "email": email,
                "name": {"first": "User", "last": "Unknown"}
            }
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.admin_url}/admin/identities",
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code == 201:
                    return {
                        "success": True,
                        "identity": response.json(),
                        "message": "Identity created successfully"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to create identity: {response.text}",
                        "status_code": response.status_code
                    }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Exception occurred: {str(e)}"
                }
    
    async def get_identity(self, identity_id: str) -> Dict[str, Any]:
        """Get an identity by ID."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.admin_url}/admin/identities/{identity_id}")
                
                if response.status_code == 200:
                    identity_data = response.json()
                    return {
                        "success": True,
                        "identity": identity_data,
                        "notion_config": self._extract_notion_config(identity_data)
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to get identity: {response.text}",
                        "status_code": response.status_code
                    }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Exception occurred: {str(e)}"
                }
    
    async def update_identity_notion_config(
        self, 
        identity_id: str, 
        notion_config: UserNotionConfig
    ) -> Dict[str, Any]:
        """Update a user's Notion configuration."""
        # First get current identity
        identity_result = await self.get_identity(identity_id)
        if not identity_result.get("success"):
            return identity_result
        
        identity_data = identity_result["identity"]
        traits = identity_data.get("traits", {})
        
        # Update traits with new Notion config
        traits.update(notion_config.to_traits())
        
        # Update identity
        payload = {
            "traits": traits,
            "schema_id": identity_data.get("schema_id", "default")
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.put(
                    f"{self.admin_url}/admin/identities/{identity_id}",
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return {
                        "success": True,
                        "identity": response.json(),
                        "message": "Notion configuration updated successfully"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to update identity: {response.text}",
                        "status_code": response.status_code
                    }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Exception occurred: {str(e)}"
                }
    
    def _extract_notion_config(self, identity_data: Dict[str, Any]) -> Optional[UserNotionConfig]:
        """Extract Notion config from identity traits."""
        traits = identity_data.get("traits", {})
        if "notion_config" in traits:
            try:
                return UserNotionConfig.from_traits(traits)
            except Exception:
                return None
        return None
    
    async def list_identities(self) -> Dict[str, Any]:
        """List all identities."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.admin_url}/admin/identities")
                
                if response.status_code == 200:
                    identities = response.json()
                    # Add notion config to each identity
                    enriched_identities = []
                    for identity in identities:
                        notion_config = self._extract_notion_config(identity)
                        identity["notion_config"] = notion_config.dict() if notion_config else None
                        enriched_identities.append(identity)
                    
                    return {
                        "success": True,
                        "identities": enriched_identities,
                        "count": len(identities)
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to list identities: {response.text}",
                        "status_code": response.status_code
                    }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Exception occurred: {str(e)}"
                }

# Singleton instance
kratos_service = KratosService()