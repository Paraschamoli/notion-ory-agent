from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from src.services.kratos_service import kratos_service

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.get("/health")
async def check_kratos_health():
    """Check Ory Kratos health status."""
    health_status = await kratos_service.get_health()
    return health_status

@router.post("/identities")
async def create_identity(
    email: str = Query(..., description="User email address"),
    first_name: Optional[str] = Query("User", description="First name"),
    last_name: Optional[str] = Query("Unknown", description="Last name")
):
    """Create a new user identity in Kratos."""
    traits = {
        "email": email,
        "name": {
            "first": first_name,
            "last": last_name
        }
    }
    
    result = await kratos_service.create_identity(email, traits)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "Failed to create identity")
        )
    
    return {
        "message": "Identity created successfully",
        "identity_id": result["identity"]["id"],
        "email": email
    }

@router.get("/identities")
async def list_identities():
    """List all identities in Kratos."""
    result = await kratos_service.list_identities()
    
    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "Failed to list identities")
        )
    
    return {
        "count": result.get("count", 0),
        "identities": result.get("identities", [])
    }

@router.get("/identities/{identity_id}")
async def get_identity(identity_id: str):
    """Get a specific identity by ID."""
    result = await kratos_service.get_identity(identity_id)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=404,
            detail=result.get("error", "Identity not found")
        )
    
    return result["identity"]

@router.get("/login/{flow_id}")
async def get_login_flow(flow_id: str):
    """Get login flow information."""
    result = await kratos_service.get_login_flow(flow_id)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=404,
            detail=result.get("error", "Login flow not found")
        )
    
    return result["flow"]