import httpx
from typing import Optional, Dict, Any
from src.config import settings

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
        """Create a new identity in Kratos."""
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
                    return {
                        "success": True,
                        "identity": response.json()
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
    
    async def list_identities(self) -> Dict[str, Any]:
        """List all identities."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.admin_url}/admin/identities")
                
                if response.status_code == 200:
                    return {
                        "success": True,
                        "identities": response.json(),
                        "count": len(response.json())
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
    
    async def get_login_flow(self, flow_id: str) -> Dict[str, Any]:
        """Get a login flow by ID."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/self-service/login/flows?id={flow_id}")
                
                if response.status_code == 200:
                    return {
                        "success": True,
                        "flow": response.json()
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to get login flow: {response.text}",
                        "status_code": response.status_code
                    }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Exception occurred: {str(e)}"
                }

# Singleton instance
kratos_service = KratosService()