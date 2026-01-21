import sys
import os

# Add src to Python path - adjust for being in tests folder
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import settings

print("Configuration loaded successfully!")
print(f"App Name: {settings.app_name}")
print(f"Ory Kratos URL: {settings.ory_kratos_url}")
print(f"Ory Hydra URL: {settings.ory_hydra_url}")
print(f"Debug Mode: {settings.debug}")