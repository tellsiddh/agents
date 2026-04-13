from agent import Agent
import json


def read_config(file_path):
    with open(file_path, "r") as file:
        return json.load(file)


def build_agents(config) -> dict[str, Agent]:
    agents_map = {}
    for cfg in config["agents"]:
        agents_map[cfg["agent_id"]] = Agent(
            agent_id=cfg["agent_id"],
            system_prompt=cfg["system_prompt"],
            tools=cfg.get("tools", []),
            can_call=cfg.get("can_call", []),
            max_steps=cfg.get("max_steps", 10),
        )
    return agents_map


if __name__ == "__main__":
    config = read_config("config.json")
    agents = build_agents(config)
    settings = config.get("agent_settings", {})
    query = (
        "I need help with a few things: "
        "1) What's the weather in Tokyo and convert the temperature to Celsius, "
        "2) Calculate the compound interest on $10,000 at 5% annual rate for 3 years (formula: 10000 * (1 + 0.05)**3), "
        "3) Find me some info about machine learning, "
        "4) Write me a short haiku inspired by what you find about the weather in Tokyo. Include the humidity value and temperature in Celsius in the haiku."
    )
    # query = "what is 55kg in lb?"
    result = agents["main"].run(
        query=query,
        agents_map=agents,
        model="openai/gpt4o_mini",
        max_depth=settings.get("max_depth", 3),
        session_id=config.get("session_id"),
        enable_history=True,
    )
    print("\n=== Final Answer ===")
    print(result)
