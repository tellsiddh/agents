from agent import Agent
import json


def read_config(file_path):
    with open(file_path, "r") as file:
        return json.load(file)


def build_agents(config):
    agents_map = {}
    tool_auth_map = {
        t["name"]: t.get("auth_ref", "internal") for t in config.get("tools", [])
    }

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
        )
    return agents_map


if __name__ == "__main__":
    config = read_config("config.json")
    agents = build_agents(config)
    settings = config.get("agent_settings", {})

    query = "Send an email to test@example.com with subject 'Hello from Agent' and body 'This is a test email from the multi-agent system.'"
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
