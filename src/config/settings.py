from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from pydantic import Field

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Application
    app_name: str = "Notion Ory Agent"
    debug: bool = False
    environment: str = "development"
    
    # Server
    mcp_server_host: str = "0.0.0.0"
    mcp_server_port: int = 8000
    
    # Ory Kratos
    ory_kratos_url: str = Field(default="http://localhost:4433")
    ory_kratos_admin_url: Optional[str] = None
    
    # Ory Hydra
    ory_hydra_url: str = Field(default="http://localhost:4444")
    ory_hydra_admin_url: Optional[str] = None
    
    # Notion - App-level defaults (for admin/fallback)
    notion_api_key: Optional[str] = None
    notion_database_id: Optional[str] = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set admin URLs if not provided
        if not self.ory_kratos_admin_url:
            self.ory_kratos_admin_url = self.ory_kratos_url.replace("4433", "4434")
        if not self.ory_hydra_admin_url:
            self.ory_hydra_admin_url = self.ory_hydra_url.replace("4444", "4445")

# Global settings instance
settings = Settings()