from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from src.services.hydra_service import hydra_service

router = APIRouter(prefix="/oauth", tags=["oauth"])

@router.get("/health")
async def check_hydra_health():
    """Check Ory Hydra health status."""
    health_status = await hydra_service.get_health()
    return health_status

@router.post("/clients")
async def create_oauth_client(
    client_name: str = Query(..., description="Client application name"),
    redirect_uris: List[str] = Query(..., description="Allowed redirect URIs"),
    grant_types: Optional[List[str]] = Query(None, description="Allowed grant types"),
    scope: Optional[str] = Query("openid offline", description="OAuth scope")
):
    """Create a new OAuth 2.0 client."""
    result = await hydra_service.create_oauth_client(
        client_name=client_name,
        redirect_uris=redirect_uris,
        grant_types=grant_types,
        scope=scope
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "Failed to create OAuth client")
        )
    
    # Don't return the full client secret in response
    response_data = {
        "message": "OAuth client created successfully",
        "client_id": result.get("client_id"),
        "client_name": result["client"].get("client_name"),
        "redirect_uris": result["client"].get("redirect_uris"),
        "scope": result["client"].get("scope")
    }
    
    return response_data

@router.get("/clients")
async def list_oauth_clients():
    """List all OAuth clients."""
    result = await hydra_service.list_oauth_clients()
    
    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "Failed to list OAuth clients")
        )
    
    return {
        "count": result.get("count", 0),
        "clients": result.get("clients", [])
    }

@router.get("/clients/{client_id}")
async def get_oauth_client(client_id: str):
    """Get a specific OAuth client by ID."""
    result = await hydra_service.get_oauth_client(client_id)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=404,
            detail=result.get("error", "OAuth client not found")
        )
    
    # Remove sensitive information
    client_data = result["client"].copy()
    if "client_secret" in client_data:
        del client_data["client_secret"]
    
    return client_data

@router.delete("/clients/{client_id}")
async def delete_oauth_client(client_id: str):
    """Delete an OAuth client."""
    result = await hydra_service.delete_oauth_client(client_id)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "Failed to delete OAuth client")
        )
    
    return {"message": f"Client {client_id} deleted successfully"}

@router.get("/consent/{consent_challenge}")
async def get_consent_request(consent_challenge: str):
    """Get OAuth consent request information."""
    result = await hydra_service.get_oauth_consent_request(consent_challenge)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=404,
            detail=result.get("error", "Consent request not found")
        )
    
    return result["consent_request"]