from typing import Annotated, TYPE_CHECKING
from fastapi import Depends
from src.config import settings

if TYPE_CHECKING:
    from src.config.settings import Settings

def get_settings() -> "Settings":
    """Dependency to get application settings."""
    return settings

# Type alias for dependency injection
SettingsDep = Annotated["Settings", Depends(get_settings)]