import httpx
from typing import Optional, Dict, Any, List
from src.config import settings

class HydraService:
    """Service for interacting with Ory Hydra."""
    
    def __init__(self):
        self.base_url = settings.ory_hydra_url
        self.admin_url = settings.ory_hydra_admin_url or self.base_url.replace("4444", "4445")
        
    async def get_health(self) -> Dict[str, Any]:
        """Check Hydra health status."""
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
    
    async def create_oauth_client(
        self,
        client_name: str,
        redirect_uris: List[str],
        grant_types: Optional[List[str]] = None,
        scope: Optional[str] = "openid offline profile notion_api"
    ) -> Dict[str, Any]:
        """Create a new OAuth 2.0 client with Notion API scope."""
        payload = {
            "client_name": client_name,
            "redirect_uris": redirect_uris,
            "grant_types": grant_types or ["authorization_code", "refresh_token"],
            "scope": scope,  # Added notion_api scope
            "token_endpoint_auth_method": "client_secret_basic"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.admin_url}/admin/clients",
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code == 201:
                    client_data = response.json()
                    return {
                        "success": True,
                        "client": client_data,
                        "message": "OAuth client created successfully",
                        "client_id": client_data.get("client_id"),
                        "client_secret": client_data.get("client_secret")
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to create client: {response.text}",
                        "status_code": response.status_code
                    }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Exception occurred: {str(e)}"
                }
    
    async def accept_oauth_consent_request(
        self,
        consent_challenge: str,
        grant_scope: List[str],
        session_data: Optional[Dict[str, Any]] = None,
        remember: bool = True
    ) -> Dict[str, Any]:
        """Accept an OAuth consent request with session data."""
        payload = {
            "grant_scope": grant_scope,
            "remember": remember,
            "remember_for": 3600,
            "session": session_data or {
                "access_token": {},
                "id_token": {}
            }
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.put(
                    f"{self.admin_url}/admin/oauth2/auth/requests/consent/accept?consent_challenge={consent_challenge}",
                    json=payload
                )
                
                if response.status_code == 200:
                    return {
                        "success": True,
                        "redirect_to": response.json().get("redirect_to"),
                        "message": "Consent accepted successfully"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to accept consent: {response.text}",
                        "status_code": response.status_code
                    }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Exception occurred: {str(e)}"
                }

# Singleton instance
hydra_service = HydraService()