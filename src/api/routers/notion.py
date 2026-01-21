from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from src.services.notion_service import notion_service

router = APIRouter(prefix="/notion", tags=["notion"])

@router.get("/health")
async def check_notion_connection():
    """Check Notion API connection."""
    connection_status = await notion_service.check_connection()
    return connection_status

@router.get("/databases/{database_id}/query")
async def query_database(
    database_id: str,
    filter_properties: Optional[List[str]] = Query(None, description="Properties to filter"),
    page_size: int = Query(100, description="Number of results per page")
):
    """Query a Notion database."""
    result = await notion_service.query_database(
        database_id=database_id,
        filter_properties=filter_properties,
        page_size=page_size
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "Failed to query database")
        )
    
    return {
        "count": result.get("count", 0),
        "has_more": result.get("has_more", False),
        "next_cursor": result.get("next_cursor"),
        "results": result.get("results", []),
        "database_id": database_id
    }

@router.post("/pages")
async def create_page(
    database_id: Optional[str] = Query(None, description="Database ID (uses default if not provided)"),
    title: str = Query("New Page", description="Page title"),
    content: Optional[str] = Query(None, description="Page content")
):
    """Create a new page in Notion."""
    properties = {
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
    
    result = await notion_service.create_page(
        database_id=database_id,
        properties=properties,
        content=content
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "Failed to create page")
        )
    
    # Remove full page data from response for brevity
    response_data = {
        "message": "Page created successfully",
        "page_id": result.get("page_id"),
        "url": result.get("url"),
        "title": title
    }
    
    return response_data

@router.get("/pages/{page_id}")
async def get_page(page_id: str):
    """Get a Notion page by ID."""
    result = await notion_service.get_page(page_id)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=404,
            detail=result.get("error", "Page not found")
        )
    
    return result["page"]

@router.patch("/pages/{page_id}")
async def update_page(
    page_id: str,
    title: Optional[str] = Query(None, description="New page title")
):
    """Update a Notion page."""
    if not title:
        raise HTTPException(
            status_code=400,
            detail="At least one property must be provided for update"
        )
    
    properties = {
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
    
    result = await notion_service.update_page(page_id, properties)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "Failed to update page")
        )
    
    return {
        "message": "Page updated successfully",
        "page_id": page_id,
        "title": title
    }

@router.get("/search")
async def search_notion(
    query: str = Query("", description="Search query"),
    filter_type: str = Query("page", description="Filter by type: 'page' or 'database'"),
    page_size: int = Query(20, description="Number of results per page")
):
    """Search in Notion."""
    result = await notion_service.search(
        query=query,
        filter_type=filter_type,
        page_size=page_size
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "Failed to search")
        )
    
    return {
        "count": result.get("count", 0),
        "has_more": result.get("has_more", False),
        "next_cursor": result.get("next_cursor"),
        "results": result.get("results", [])
    }