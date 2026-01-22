from pydantic import BaseModel, Field, SecretStr
from typing import Optional, Dict, Any
from datetime import datetime

class UserNotionConfig(BaseModel):
    """User-specific Notion configuration stored in Kratos identity traits."""
    notion_api_key: SecretStr = Field(
        ...,
        description="User's Notion API key (encrypted in storage)"
    )
    notion_database_id: Optional[str] = Field(
        None,
        description="User's default Notion database ID"
    )
    enabled: bool = Field(
        default=True,
        description="Whether Notion integration is enabled for this user"
    )
    connected_at: Optional[datetime] = Field(
        None,
        description="When the Notion connection was last verified"
    )
    
    def to_traits(self) -> Dict[str, Any]:
        """Convert to format suitable for Kratos traits."""
        return {
            "notion_config": {
                "api_key": self.notion_api_key.get_secret_value(),
                "database_id": self.notion_database_id,
                "enabled": self.enabled,
                "connected_at": self.connected_at.isoformat() if self.connected_at else None
            }
        }
    
    @classmethod
    def from_traits(cls, traits: Dict[str, Any]) -> "UserNotionConfig":
        """Create from Kratos traits."""
        notion_config = traits.get("notion_config", {})
        return cls(
            notion_api_key=SecretStr(notion_config.get("api_key", "")),
            notion_database_id=notion_config.get("database_id"),
            enabled=notion_config.get("enabled", True),
            connected_at=datetime.fromisoformat(notion_config["connected_at"]) 
                if notion_config.get("connected_at") else None
        )

class NotionConnectionTest(BaseModel):
    """Result of testing Notion connection."""
    status: str = Field(..., description="Connection status: connected, error")
    user_id: Optional[str] = Field(None, description="Notion user ID")
    user_name: Optional[str] = Field(None, description="Notion user name")
    workspace_name: Optional[str] = Field(None, description="Notion workspace name")
    error: Optional[str] = Field(None, description="Error message if failed")
    tested_at: datetime = Field(default_factory=datetime.now)