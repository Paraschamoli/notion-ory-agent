from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings
from .routers import health, auth, oauth, notion  # Add notion import
from src.mcp.api import router as mcp_router

def create_app() -> FastAPI:
    """Application factory function."""
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        debug=settings.debug,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.debug else [],  # Be restrictive in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(oauth.router)
    app.include_router(notion.router)  # Add this line
    app.include_router(mcp_router)
    
    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "message": f"Welcome to {settings.app_name}",
            "version": "0.1.0",
            "docs": "/docs" if settings.debug else None,
            "mcp_ws": "/mcp/ws",
            "auth_endpoints": "/auth/*",
            "oauth_endpoints": "/oauth/*",
            "notion_endpoints": "/notion/*"
        }
    
    return app