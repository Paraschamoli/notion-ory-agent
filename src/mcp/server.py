from typing import Any, List
import mcp.types as types
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
from src.config import settings
from src.services.kratos_service import kratos_service
from src.services.hydra_service import hydra_service
# Removed: from src.services.notion_service import notion_service
from src.services.user_notion_service import user_notion_service
from src.models.user_notion import UserNotionConfig

class MCPServer:
    """Main MCP server class."""
    
    def __init__(self):
        self.server = Server("notion-ory-agent")
        
    async def initialize(self):
        """Initialize the MCP server with tools and resources."""
        # Register tools
        self.server.list_tools(self.handle_list_tools)
        self.server.call_tool(self.handle_call_tool)
        
        # Register resources
        self.server.list_resources(self.handle_list_resources)
        self.server.read_resource(self.handle_read_resource)
        
        # Register prompts
        self.server.list_prompts(self.handle_list_prompts)
        self.server.get_prompt(self.handle_get_prompt)
        
        # Set notification options
        notification_options = NotificationOptions()
        
        return InitializationOptions(
            server_name="Notion Ory Agent",
            server_version="0.1.0",
            capabilities=self.server.get_capabilities(
                notification_options=notification_options,
                experimental_capabilities={},
            ),
        )
    
    async def handle_list_tools(self) -> List[types.Tool]:
        """List available tools."""
        return [
            types.Tool(
                name="health_check",
                description="Check the health status of the application",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
            types.Tool(
                name="get_config",
                description="Get current application configuration",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
            # Kratos tools
            types.Tool(
                name="check_kratos_health",
                description="Check Ory Kratos health status",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
            types.Tool(
                name="list_kratos_identities",
                description="List all user identities in Kratos",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
            types.Tool(
                name="create_kratos_identity",
                description="Create a new user identity in Kratos",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "email": {
                            "type": "string",
                            "description": "User email address"
                        },
                        "first_name": {
                            "type": "string",
                            "description": "First name (optional)",
                            "default": "User"
                        },
                        "last_name": {
                            "type": "string",
                            "description": "Last name (optional)",
                            "default": "Unknown"
                        }
                    },
                    "required": ["email"]
                },
            ),
            # Hydra tools
            types.Tool(
                name="check_hydra_health",
                description="Check Ory Hydra health status",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
            types.Tool(
                name="list_oauth_clients",
                description="List all OAuth clients in Hydra",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
            types.Tool(
                name="create_oauth_client",
                description="Create a new OAuth 2.0 client in Hydra",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "client_name": {
                            "type": "string",
                            "description": "Client application name"
                        },
                        "redirect_uris": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Allowed redirect URIs (comma-separated)"
                        },
                        "scope": {
                            "type": "string",
                            "description": "OAuth scope (optional)",
                            "default": "openid offline"
                        }
                    },
                    "required": ["client_name", "redirect_uris"]
                },
            ),
            # Notion tools (updated for user-specific access)
            types.Tool(
                name="check_notion_connection",
                description="Check Notion API connection for a specific user",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "User ID from Kratos"
                        }
                    },
                    "required": ["user_id"]
                },
            ),
            types.Tool(
                name="search_notion",
                description="Search in a user's Notion workspace",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "User ID from Kratos"
                        },
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        },
                        "filter_type": {
                            "type": "string",
                            "description": "Filter by type: 'page' or 'database'",
                            "default": "page"
                        }
                    },
                    "required": ["user_id", "query"]
                },
            ),
            types.Tool(
                name="create_notion_page",
                description="Create a new page in user's Notion",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "User ID from Kratos"
                        },
                        "title": {
                            "type": "string",
                            "description": "Page title"
                        },
                        "content": {
                            "type": "string",
                            "description": "Page content (optional)"
                        },
                        "database_id": {
                            "type": "string",
                            "description": "Database ID (optional, uses user's default if not provided)"
                        }
                    },
                    "required": ["user_id", "title"]
                },
            ),
            types.Tool(
                name="query_notion_database",
                description="Query a Notion database for a specific user",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "User ID from Kratos"
                        },
                        "database_id": {
                            "type": "string",
                            "description": "Database ID (optional, uses user's default if not provided)"
                        },
                        "page_size": {
                            "type": "number",
                            "description": "Number of results",
                            "default": 10
                        }
                    },
                    "required": ["user_id"]
                },
            ),
            # User-specific Notion tools
            types.Tool(
                name="configure_user_notion",
                description="Configure Notion integration for a user",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "User ID from Kratos"
                        },
                        "api_key": {
                            "type": "string",
                            "description": "User's Notion API key"
                        },
                        "database_id": {
                            "type": "string",
                            "description": "User's default Notion database ID (optional)"
                        }
                    },
                    "required": ["user_id", "api_key"]
                },
            ),
            types.Tool(
                name="create_user_notion_page",
                description="Create a page in user's Notion database",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "User ID from Kratos"
                        },
                        "title": {
                            "type": "string",
                            "description": "Page title"
                        },
                        "content": {
                            "type": "string",
                            "description": "Page content (optional)"
                        },
                        "database_id": {
                            "type": "string",
                            "description": "Database ID (optional, uses user's default)"
                        }
                    },
                    "required": ["user_id", "title"]
                },
            ),
        ]
    
    async def handle_call_tool(
        self, name: str, arguments: dict[str, Any] | None
    ) -> List[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """Handle tool calls."""
        if name == "health_check":
            return [
                types.TextContent(
                    type="text",
                    text=f"Application is healthy\nName: {settings.app_name}\nEnvironment: {settings.environment}"
                )
            ]
        elif name == "get_config":
            return [
                types.TextContent(
                    type="text",
                    text=f"Configuration:\nDebug: {settings.debug}\nPort: {settings.mcp_server_port}\nHost: {settings.mcp_server_host}"
                )
            ]
        # Kratos tools
        elif name == "check_kratos_health":
            health_status = await kratos_service.get_health()
            return [
                types.TextContent(
                    type="text",
                    text=f"Kratos Health: {health_status.get('status', 'unknown')}\n"
                         f"Status Code: {health_status.get('status_code', 'N/A')}"
                )
            ]
        elif name == "list_kratos_identities":
            result = await kratos_service.list_identities()
            if result.get("success"):
                count = result.get("count", 0)
                return [
                    types.TextContent(
                        type="text",
                        text=f"Found {count} identities in Kratos"
                    )
                ]
            else:
                return [
                    types.TextContent(
                        type="text",
                        text=f"Error listing identities: {result.get('error', 'Unknown error')}"
                    )
                ]
        elif name == "create_kratos_identity":
            if not arguments:
                raise ValueError("Arguments required for create_kratos_identity")
            
            email = arguments.get("email")
            first_name = arguments.get("first_name", "User")
            last_name = arguments.get("last_name", "Unknown")
            
            traits = {
                "email": email,
                "name": {
                    "first": first_name,
                    "last": last_name
                }
            }
            
            result = await kratos_service.create_identity(email, traits)
            
            if result.get("success"):
                identity_id = result["identity"]["id"]
                return [
                    types.TextContent(
                        type="text",
                        text=f"✅ Identity created successfully!\n"
                             f"ID: {identity_id}\n"
                             f"Email: {email}"
                    )
                ]
            else:
                return [
                    types.TextContent(
                        type="text",
                        text=f"❌ Failed to create identity: {result.get('error', 'Unknown error')}"
                    )
                ]
        # Hydra tools
        elif name == "check_hydra_health":
            health_status = await hydra_service.get_health()
            return [
                types.TextContent(
                    type="text",
                    text=f"Hydra Health: {health_status.get('status', 'unknown')}\n"
                         f"Status Code: {health_status.get('status_code', 'N/A')}"
                )
            ]
        elif name == "list_oauth_clients":
            result = await hydra_service.list_oauth_clients()
            if result.get("success"):
                count = result.get("count", 0)
                return [
                    types.TextContent(
                        type="text",
                        text=f"Found {count} OAuth clients in Hydra"
                    )
                ]
            else:
                return [
                    types.TextContent(
                        type="text",
                        text=f"Error listing OAuth clients: {result.get('error', 'Unknown error')}"
                    )
                ]
        elif name == "create_oauth_client":
            if not arguments:
                raise ValueError("Arguments required for create_oauth_client")
            
            client_name = arguments.get("client_name")
            
            # Handle redirect_uris which might come as string or array
            redirect_uris_input = arguments.get("redirect_uris", [])
            if isinstance(redirect_uris_input, str):
                # Convert comma-separated string to list
                redirect_uris = [uri.strip() for uri in redirect_uris_input.split(",")]
            else:
                redirect_uris = redirect_uris_input
            
            scope = arguments.get("scope", "openid offline")
            
            result = await hydra_service.create_oauth_client(
                client_name=client_name,
                redirect_uris=redirect_uris,
                scope=scope
            )
            
            if result.get("success"):
                client_id = result.get("client_id")
                return [
                    types.TextContent(
                        type="text",
                        text=f"✅ OAuth client created successfully!\n"
                             f"Client ID: {client_id}\n"
                             f"Client Name: {client_name}\n"
                             f"Redirect URIs: {', '.join(redirect_uris)}"
                    )
                ]
            else:
                return [
                    types.TextContent(
                        type="text",
                        text=f"❌ Failed to create OAuth client: {result.get('error', 'Unknown error')}"
                    )
                ]
        # Notion tools - UPDATED FOR USER-SPECIFIC ACCESS
        elif name == "check_notion_connection":
            if not arguments:
                raise ValueError("Arguments required for check_notion_connection")
            
            user_id = arguments.get("user_id")
            if not user_id:
                return [
                    types.TextContent(
                        type="text",
                        text="❌ User ID is required. Use 'configure_user_notion' first to set up a user's Notion connection."
                    )
                ]
            
            # Get user config from Kratos
            user_result = await kratos_service.get_identity(user_id)
            if not user_result.get("success"):
                return [
                    types.TextContent(
                        type="text",
                        text=f"❌ User {user_id} not found in Kratos"
                    )
                ]
            
            notion_config = user_result.get("notion_config")
            if not notion_config:
                return [
                    types.TextContent(
                        type="text",
                        text=f"❌ User {user_id} has no Notion configuration. Use 'configure_user_notion' first."
                    )
                ]
            
            # Test the connection
            test_result = await user_notion_service.test_user_connection(notion_config)
            
            if test_result.status == "connected":
                return [
                    types.TextContent(
                        type="text",
                        text=f"✅ User {user_id} is connected to Notion!\n"
                             f"User: {test_result.user_name}\n"
                             f"Workspace: {test_result.workspace_name}\n"
                             f"Last tested: {test_result.tested_at}"
                    )
                ]
            else:
                return [
                    types.TextContent(
                        type="text",
                        text=f"❌ User {user_id} Notion connection failed: {test_result.error}"
                    )
                ]
        
        elif name == "search_notion":
            if not arguments:
                raise ValueError("Arguments required for search_notion")
            
            user_id = arguments.get("user_id")
            query = arguments.get("query", "")
            filter_type = arguments.get("filter_type", "page")
            
            if not user_id:
                return [
                    types.TextContent(
                        type="text",
                        text="❌ User ID is required. Use 'configure_user_notion' first to set up a user's Notion connection."
                    )
                ]
            
            # Get user config from Kratos
            user_result = await kratos_service.get_identity(user_id)
            if not user_result.get("success"):
                return [
                    types.TextContent(
                        type="text",
                        text=f"❌ User {user_id} not found in Kratos"
                    )
                ]
            
            notion_config = user_result.get("notion_config")
            if not notion_config:
                return [
                    types.TextContent(
                        type="text",
                        text=f"❌ User {user_id} has no Notion configuration. Use 'configure_user_notion' first."
                    )
                ]
            
            # Use user_notion_service with the user's config
            result = await user_notion_service.search(
                notion_config=notion_config,
                query=query,
                filter_type=filter_type
            )
            
            if result.get("success"):
                count = result.get("count", 0)
                if count > 0:
                    results_text = f"Found {count} results for '{query}':\n"
                    for i, item in enumerate(result.get("results", [])[:5], 1):
                        item_type = item.get("object", "unknown")
                        title = "Untitled"
                        
                        # Try to get title from various properties
                        if item_type == "page":
                            props = item.get("properties", {})
                            if "Name" in props and "title" in props["Name"]:
                                titles = props["Name"]["title"]
                                if titles:
                                    title = titles[0].get("plain_text", "Untitled")
                            elif "title" in props:
                                titles = props["title"]["title"]
                                if titles:
                                    title = titles[0].get("plain_text", "Untitled")
                        
                        results_text += f"{i}. {title} ({item_type})\n"
                    
                    if count > 5:
                        results_text += f"... and {count - 5} more results"
                    
                    return [
                        types.TextContent(
                            type="text",
                            text=results_text
                        )
                    ]
                else:
                    return [
                        types.TextContent(
                            type="text",
                            text=f"No results found for '{query}'"
                        )
                    ]
            else:
                return [
                    types.TextContent(
                        type="text",
                        text=f"❌ Search failed: {result.get('error', 'Unknown error')}"
                    )
                ]
        
        elif name == "create_notion_page":
            if not arguments:
                raise ValueError("Arguments required for create_notion_page")
            
            user_id = arguments.get("user_id")
            title = arguments.get("title", "New Page")
            content = arguments.get("content")
            database_id = arguments.get("database_id")
            
            if not user_id:
                return [
                    types.TextContent(
                        type="text",
                        text="❌ User ID is required. Use 'configure_user_notion' first to set up a user's Notion connection."
                    )
                ]
            
            # Get user config from Kratos
            user_result = await kratos_service.get_identity(user_id)
            if not user_result.get("success"):
                return [
                    types.TextContent(
                        type="text",
                        text=f"❌ User {user_id} not found in Kratos"
                    )
                ]
            
            notion_config = user_result.get("notion_config")
            if not notion_config:
                return [
                    types.TextContent(
                        type="text",
                        text=f"❌ User {user_id} has no Notion configuration. Use 'configure_user_notion' first."
                    )
                ]
            
            # Use user's database_id if not provided
            if not database_id and notion_config.notion_database_id:
                database_id = notion_config.notion_database_id
            
            result = await user_notion_service.create_page(
                notion_config=notion_config,
                database_id=database_id,
                properties={
                    "Name": {
                        "title": [
                            {
                                "text": {
                                    "content": title
                                }
                            }
                        ]
                    }
                },
                content=content
            )
            
            if result.get("success"):
                page_id = result.get("page_id")
                url = result.get("url")
                return [
                    types.TextContent(
                        type="text",
                        text=f"✅ Page created successfully for user {user_id}!\n"
                             f"Title: {title}\n"
                             f"ID: {page_id}\n"
                             f"URL: {url}"
                    )
                ]
            else:
                return [
                    types.TextContent(
                        type="text",
                        text=f"❌ Failed to create page: {result.get('error', 'Unknown error')}"
                    )
                ]
        
        elif name == "query_notion_database":
            user_id = arguments.get("user_id") if arguments else None
            database_id = arguments.get("database_id") if arguments else None
            page_size = arguments.get("page_size", 10) if arguments else 10
            
            if not user_id:
                return [
                    types.TextContent(
                        type="text",
                        text="❌ User ID is required. Use 'configure_user_notion' first to set up a user's Notion connection."
                    )
                ]
            
            # Get user config from Kratos
            user_result = await kratos_service.get_identity(user_id)
            if not user_result.get("success"):
                return [
                    types.TextContent(
                        type="text",
                        text=f"❌ User {user_id} not found in Kratos"
                    )
                ]
            
            notion_config = user_result.get("notion_config")
            if not notion_config:
                return [
                    types.TextContent(
                        type="text",
                        text=f"❌ User {user_id} has no Notion configuration. Use 'configure_user_notion' first."
                    )
                ]
            
            # Use user's database_id if not provided
            if not database_id and notion_config.notion_database_id:
                database_id = notion_config.notion_database_id
            
            result = await user_notion_service.query_database(
                notion_config=notion_config,
                database_id=database_id,
                page_size=page_size
            )
            
            if result.get("success"):
                count = result.get("count", 0)
                if count > 0:
                    results_text = f"Found {count} pages in database:\n"
                    for i, page in enumerate(result.get("results", [])[:5], 1):
                        props = page.get("properties", {})
                        title = "Untitled"
                        
                        if "Name" in props and "title" in props["Name"]:
                            titles = props["Name"]["title"]
                            if titles:
                                title = titles[0].get("plain_text", "Untitled")
                        elif "title" in props:
                            titles = props["title"]["title"]
                            if titles:
                                title = titles[0].get("plain_text", "Untitled")
                        
                        results_text += f"{i}. {title}\n"
                    
                    if count > 5:
                        results_text += f"... and {count - 5} more pages"
                    
                    return [
                        types.TextContent(
                            type="text",
                            text=results_text
                        )
                    ]
                else:
                    return [
                        types.TextContent(
                            type="text",
                            text="Database is empty or no pages found"
                        )
                    ]
            else:
                return [
                    types.TextContent(
                        type="text",
                        text=f"❌ Failed to query database: {result.get('error', 'Unknown error')}"
                    )
                ]
        
        # User-specific Notion tools
        elif name == "configure_user_notion":
            if not arguments:
                raise ValueError("Arguments required for configure_user_notion")
            
            user_id = arguments.get("user_id")
            api_key = arguments.get("api_key")
            database_id = arguments.get("database_id")
            
            # Create config and test connection
            notion_config = UserNotionConfig(
                notion_api_key=api_key,
                notion_database_id=database_id
            )
            
            test_result = await user_notion_service.test_user_connection(notion_config)
            
            if test_result.status == "connected":
                return [
                    types.TextContent(
                        type="text",
                        text=f"✅ Notion configured for user {user_id}!\n"
                             f"Connected as: {test_result.user_name}\n"
                             f"Workspace: {test_result.workspace_name}"
                    )
                ]
            else:
                return [
                    types.TextContent(
                        type="text",
                        text=f"❌ Failed to configure Notion: {test_result.error}"
                    )
                ]
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    async def handle_list_resources(self) -> List[types.Resource]:
        """List available resources."""
        return [
            types.Resource(
                uri="app://config",
                name="Application Configuration",
                description="Current application configuration",
                mimeType="text/plain",
            ),
            types.Resource(
                uri="app://health",
                name="Health Status",
                description="Application health information",
                mimeType="text/plain",
            ),
            # Kratos resources
            types.Resource(
                uri="kratos://health",
                name="Kratos Health",
                description="Ory Kratos health status",
                mimeType="text/plain",
            ),
            # Hydra resources
            types.Resource(
                uri="hydra://health",
                name="Hydra Health",
                description="Ory Hydra health status",
                mimeType="text/plain",
            ),
            # Notion resources - Updated description
            types.Resource(
                uri="notion://connection",
                name="Notion Connection Help",
                description="Information about user-specific Notion connections",
                mimeType="text/plain",
            ),
        ]
    
    async def handle_read_resource(self, uri: str) -> str:
        """Read resource content."""
        if uri == "app://config":
            return f"App Name: {settings.app_name}\nEnvironment: {settings.environment}\nDebug: {settings.debug}"
        elif uri == "app://health":
            return "Application is healthy and running"
        elif uri == "kratos://health":
            health_status = await kratos_service.get_health()
            return f"Kratos Status: {health_status.get('status', 'unknown')}"
        elif uri == "hydra://health":
            health_status = await hydra_service.get_health()
            return f"Hydra Status: {health_status.get('status', 'unknown')}"
        elif uri == "notion://connection":
            return ("Notion integration is now user-specific.\n"
                    "Users must configure their own Notion API keys.\n"
                    "Use 'configure_user_notion' tool to set up a user's Notion connection.\n"
                    "Then use other Notion tools with the 'user_id' parameter.")
        else:
            raise ValueError(f"Unknown resource: {uri}")
    
    async def handle_list_prompts(self) -> List[types.Prompt]:
        """List available prompts."""
        return [
            types.Prompt(
                name="welcome",
                description="Welcome message and instructions",
                arguments=[],
            ),
            # Authentication prompt
            types.Prompt(
                name="authentication_help",
                description="Get help with authentication using Ory Kratos",
                arguments=[],
            ),
            # OAuth prompt
            types.Prompt(
                name="oauth_help",
                description="Get help with OAuth 2.0 using Ory Hydra",
                arguments=[],
            ),
            # Notion prompt - Updated description
            types.Prompt(
                name="notion_help",
                description="Get help with user-specific Notion integration",
                arguments=[],
            ),
        ]
    
    async def handle_get_prompt(self, name: str, arguments: dict[str, str] | None) -> types.GetPromptResult:
        """Get prompt content."""
        if name == "welcome":
            return types.GetPromptResult(
                description="Welcome to Notion Ory Agent",
                messages=[
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(
                            type="text",
                            text=f"Welcome to {settings.app_name}! This agent integrates Notion with Ory Kratos and Hydra for authentication and authorization."
                        )
                    )
                ]
            )
        elif name == "authentication_help":
            return types.GetPromptResult(
                description="Authentication Help",
                messages=[
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(
                            type="text",
                            text="I can help you with authentication using Ory Kratos. You can:\n"
                                 "1. Create new user identities\n"
                                 "2. List existing identities\n"
                                 "3. Check Kratos health status\n"
                                 f"Kratos URL: {settings.ory_kratos_url}"
                        )
                    )
                ]
            )
        elif name == "oauth_help":
            return types.GetPromptResult(
                description="OAuth Help",
                messages=[
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(
                            type="text",
                            text="I can help you with OAuth 2.0 using Ory Hydra. You can:\n"
                                 "1. Create OAuth clients\n"
                                 "2. List existing OAuth clients\n"
                                 "3. Check Hydra health status\n"
                                 "4. Manage consent requests\n"
                                 f"Hydra URL: {settings.ory_hydra_url}"
                        )
                    )
                ]
            )
        elif name == "notion_help":
            return types.GetPromptResult(
                description="Notion Help",
                messages=[
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(
                            type="text",
                            text="I can help you with user-specific Notion integration. You can:\n"
                                 "1. Configure Notion for a user (requires user's API key)\n"
                                 "2. Search in a user's Notion workspace\n"
                                 "3. Create pages in a user's Notion\n"
                                 "4. Query a user's Notion databases\n"
                                 "All Notion operations now require a user_id parameter."
                        )
                    )
                ]
            )
        raise ValueError(f"Unknown prompt: {name}")

async def run_mcp_server():
    """Run the MCP server over stdio."""
    mcp_server = MCPServer()
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await mcp_server.server.run(
            read_stream,
            write_stream,
            mcp_server.initialize(),
        )