import asyncio
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.mcp.server import run_mcp_server

if __name__ == "__main__":
    try:
        asyncio.run(run_mcp_server())
    except KeyboardInterrupt:
        print("\nMCP server stopped.")