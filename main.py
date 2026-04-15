from agent import Agent
import json
from tools import register_mcp_server


def read_config(file_path):
    with open(file_path, "r") as file:
        return json.load(file)


def build_agents(config):
    agents_map = {}
    tool_auth_map = {
        t["name"]: t.get("auth_ref", "internal") for t in config.get("tools", [])
    }

    # Register all MCP servers globally
    for server_name, server_cfg in config.get("mcp", {}).items():
        register_mcp_server(server_name, server_cfg)

    for cfg in config["agents"]:
        agent_tools = cfg.get("tools", [])
        internal_tools = [
            t for t in agent_tools if tool_auth_map.get(t, "internal") == "internal"
        ]
        composio_tools = [
            t for t in agent_tools if tool_auth_map.get(t, "internal") == "composio"
        ]

        agents_map[cfg["agent_id"]] = Agent(
            agent_id=cfg["agent_id"],
            system_prompt=cfg["system_prompt"],
            tools=internal_tools,
            can_call=cfg.get("can_call", []),
            max_steps=cfg.get("max_steps", 10),
            composio_tools=composio_tools,
            mcp_servers=cfg.get("mcp_servers", []),
        )
    return agents_map


if __name__ == "__main__":
    config = read_config("config.json")
    agents = build_agents(config)
    settings = config.get("agent_settings", {})

    query = "Create a draft email to test@example.com with subject 'Hello from Agent' and body 'This is a test email from the multi-agent system.'"
    query = "what is 3 + 5 ?"
    query = "Analyze this text: 'The quick brown fox jumps over the lazy dog. The dog barked loudly.' Then tell me what 15% of the word count is."
    query = "What is the current time in mst."
    print("session_id:", config.get("session_id"))
    result = agents["main"].run(
        query=query,
        agents_map=agents,
        model="openai/gpt4o_mini",
        max_depth=settings.get("max_depth", 3),
        session_id=config.get("session_id"),
        enable_history=True,
        entity_id=config.get("entity_id", "default"),
    )

    print("\n=== Final Answer ===")
    print(result)
