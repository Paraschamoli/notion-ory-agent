from fastapi import APIRouter, Depends, HTTPException, Query, Header
from typing import Optional, List
# from src.services.notion_service import notion_service  # Removed
from src.services.user_notion_service import user_notion_service
from src.services.kratos_service import kratos_service
from src.models.user_notion import UserNotionConfig

router = APIRouter(prefix="/notion", tags=["notion"])

@router.get("/health")
async def check_notion_connection(
    x_user_id: Optional[str] = Header(None, description="Authenticated user ID")
):
    """Check Notion API connection (user-specific only)."""
    if x_user_id:
        # User-specific check
        user_result = await kratos_service.get_identity(x_user_id)
        if not user_result.get("success"):
            raise HTTPException(status_code=404, detail="User not found")
        
        notion_config = user_result.get("notion_config")
        if not notion_config or not notion_config.enabled:
            raise HTTPException(
                status_code=400, 
                detail="User has no Notion configuration or it's disabled"
            )
        
        test_result = await user_notion_service.test_user_connection(notion_config)
        return {
            "user_id": x_user_id,
            "connection": test_result.dict()
        }
    else:
        # No app-level check available anymore - require user ID
        raise HTTPException(
            status_code=400,
            detail="Notion integration is now user-specific. Please provide x-user-id header with a valid user ID."
        )

@router.post("/users/{user_id}/config")
async def configure_user_notion(
    user_id: str,
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
        user_id, 
        notion_config
    )
    
    if not update_result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=update_result.get("error", "Failed to update user configuration")
        )
    
    return {
        "message": "Notion configuration updated successfully",
        "user_id": user_id,
        "connection_test": test_result.dict(),
        "notion_user": {
            "id": test_result.user_id,
            "name": test_result.user_name,
            "workspace": test_result.workspace_name
        }
    }

@router.get("/users/{user_id}/databases/query")
async def query_user_database(
    user_id: str,
    database_id: Optional[str] = Query(None, description="Database ID (uses user's default if not provided)"),
    page_size: int = Query(100, description="Number of results per page")
):
    """Query a user's Notion database."""
    # Get user's Notion config
    user_result = await kratos_service.get_identity(user_id)
    if not user_result.get("success"):
        raise HTTPException(status_code=404, detail="User not found")
    
    notion_config = user_result.get("notion_config")
    if not notion_config or not notion_config.enabled:
        raise HTTPException(
            status_code=400, 
            detail="User has no Notion configuration or it's disabled"
        )
    
    # Query database
    result = await user_notion_service.query_user_database(
        notion_config,
        database_id=database_id,
        page_size=page_size
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "Failed to query database")
        )
    
    return {
        "user_id": user_id,
        "user_owned": True,
        "count": result.get("count", 0),
        "has_more": result.get("has_more", False),
        "next_cursor": result.get("next_cursor"),
        "database_id": database_id or notion_config.notion_database_id
    }

@router.post("/users/{user_id}/pages")
async def create_user_page(
    user_id: str,
    title: str = Query("New Page", description="Page title"),
    content: Optional[str] = Query(None, description="Page content"),
    database_id: Optional[str] = Query(None, description="Database ID (uses user's default if not provided)")
):
    """Create a new page in user's Notion database."""
    # Get user's Notion config
    user_result = await kratos_service.get_identity(user_id)
    if not user_result.get("success"):
        raise HTTPException(status_code=404, detail="User not found")
    
    notion_config = user_result.get("notion_config")
    if not notion_config or not notion_config.enabled:
        raise HTTPException(
            status_code=400, 
            detail="User has no Notion configuration or it's disabled"
        )
    
    # Create page
    result = await user_notion_service.create_user_page(
        notion_config,
        database_id=database_id,
        title=title,
        content=content
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "Failed to create page")
        )
    
    return {
        "message": "Page created successfully",
        "user_id": user_id,
        "user_owned": True,
        "page_id": result.get("page_id"),
        "url": result.get("url"),
        "title": title
    }