import json
import asyncio
from fastmcp import Client

MCP_SERVERS = {}
# Maps tool_name -> server_name for routing
_TOOL_SERVER_MAP = {}


def register_mcp_server(name, connection_config):
    MCP_SERVERS[name] = connection_config


def register_mcp_tool(tool_name, server_name):
    """Register which server a named MCP tool belongs to."""
    _TOOL_SERVER_MAP[tool_name] = server_name


def get_server_for_tool(tool_name):
    return _TOOL_SERVER_MAP.get(tool_name)


def get_mcp_tools(server_name):
    """Fetch tool schemas from an MCP server and return OpenAI-compatible schemas."""
    config = MCP_SERVERS.get(server_name)
    if not config:
        return []

    url = config["url"]

    async def _list():
        async with Client(url) as client:
            return await client.list_tools()

    try:
        tools = asyncio.run(_list())
    except Exception as e:
        print(f"[mcp_tools] Failed to list tools from '{server_name}': {e}")
        return []

    schemas = []
    for t in tools:
        schema = {
            "type": "function",
            "function": {
                "name": t.name,
                "description": t.description or "",
                "parameters": t.inputSchema
                or {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        }
        schemas.append(schema)
    return schemas


def execute_mcp_tool(server_name, tool_name, arguments):
    """Call a tool on the MCP server and return the result as a string."""
    config = MCP_SERVERS.get(server_name)
    if not config:
        return json.dumps({"error": f"MCP server '{server_name}' not registered"})

    url = config["url"]

    async def _call():
        async with Client(url) as client:
            return await client.call_tool(tool_name, arguments)

    try:
        result = asyncio.run(_call())
    except Exception as e:
        return json.dumps({"error": str(e)})

    if result:
        content = result.content if hasattr(result, "content") else result
        if isinstance(content, list) and content:
            first = content[0]
            if hasattr(first, "text"):
                return first.text
            return str(first)
        return str(content)
    return json.dumps({"result": None})


def list_mcp_servers():
    return list(MCP_SERVERS.keys())
