from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from src.services.kratos_service import kratos_service
from src.models.user_notion import UserNotionConfig
from src.services.user_notion_service import user_notion_service

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

@router.post("/{identity_id}/notion/config")
async def configure_user_notion(
    identity_id: str,
    api_key: str = Query(..., description="User's Notion API key"),
    database_id: Optional[str] = Query(None, description="User's default Notion database ID")
):
    """Configure Notion integration for a specific user."""
    # Create user notion config
    notion_config = UserNotionConfig(
        notion_api_key=api_key,
        notion_database_id=database_id
    )
    
    # Test the connection first
    test_result = await user_notion_service.test_user_connection(notion_config)
    if test_result.status != "connected":
        raise HTTPException(
            status_code=400,
            detail=f"Notion connection failed: {test_result.error}"
        )
    
    # Update connection timestamp
    notion_config.connected_at = test_result.tested_at
    
    # Save to user's Kratos identity
    update_result = await kratos_service.update_identity_notion_config(
        identity_id, 
        notion_config
    )
    
    if not update_result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=update_result.get("error", "Failed to update user configuration")
        )
    
    return {
        "message": "Notion configuration updated successfully",
        "user_id": identity_id,
        "connection_test": test_result.dict(),
        "notion_user": {
            "id": test_result.user_id,
            "name": test_result.user_name,
            "workspace": test_result.workspace_name
        }
    }

@router.get("/{identity_id}/notion/status")
async def get_user_notion_status(identity_id: str):
    """Get a user's Notion configuration status."""
    user_result = await kratos_service.get_identity(identity_id)
    
    if not user_result.get("success"):
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    notion_config = user_result.get("notion_config")
    
    if not notion_config:
        return {
            "user_id": identity_id,
            "notion_configured": False,
            "message": "User has no Notion configuration"
        }
    
    # Test current connection
    test_result = await user_notion_service.test_user_connection(notion_config)
    
    return {
        "user_id": identity_id,
        "notion_configured": True,
        "enabled": notion_config.enabled,
        "connected_at": notion_config.connected_at,
        "connection_test": test_result.dict(),
        "has_default_database": notion_config.notion_database_id is not None
    }