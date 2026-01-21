from fastapi import APIRouter, WebSocket
import json
from .server import MCPServer

router = APIRouter(prefix="/mcp", tags=["mcp"])

@router.websocket("/ws")
async def mcp_websocket(websocket: WebSocket):
    """WebSocket endpoint for MCP communication."""
    await websocket.accept()
    
    mcp_server = MCPServer()
    initialization_result = await mcp_server.initialize()
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Here we would handle MCP protocol messages
            # For now, just echo back
            await websocket.send_text(json.dumps({
                "type": "response",
                "content": f"Received: {message}"
            }))
            
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()

@router.get("/tools")
async def list_mcp_tools():
    """List available MCP tools."""
    mcp_server = MCPServer()
    tools = await mcp_server.handle_list_tools()
    return {"tools": tools}

@router.get("/resources")
async def list_mcp_resources():
    """List available MCP resources."""
    mcp_server = MCPServer()
    resources = await mcp_server.handle_list_resources()
    return {"resources": resources}