import uvicorn
from src.config import settings
from src.api.main import create_app

# Create the app instance
app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        app,  # Pass the app instance directly
        host=settings.mcp_server_host,
        port=settings.mcp_server_port,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info"
    )