import json

MCP_SERVERS = {}


def register_mcp_server(name, connection_config):
    MCP_SERVERS[name] = connection_config


def get_mcp_tools(server_name):
    return []


def execute_mcp_tool(server_name, tool_name, arguments):
    return json.dumps({"error": "MCP integration not yet implemented"})


def list_mcp_servers():
    return list(MCP_SERVERS.keys())
