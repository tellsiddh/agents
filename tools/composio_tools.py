import json
import os
from dotenv import load_dotenv
from environs import composio_toolkit_versions

load_dotenv()

from composio import Composio
from composio_openai import OpenAIProvider

COMPOSIO_CLIENT = None


def get_composio_client():
    provider = OpenAIProvider()
    api_key = os.getenv("COMPOSIO_API_KEY")
    COMPOSIO_CLIENT = Composio(
        provider=provider, api_key=api_key, toolkit_versions=composio_toolkit_versions
    )
    return COMPOSIO_CLIENT


def get_composio_tools(actions, entity_id="default"):

    try:
        client = get_composio_client()
        tools = []
        tool_names = [a for a in actions if "_" in a]
        toolkit_names = [a for a in actions if "_" not in a]
        if tool_names:
            try:
                fetched_tools = client.tools.get(user_id=entity_id, tools=tool_names)
                tools.extend(fetched_tools)
            except Exception as e:
                print(f"Warning: Could not load specific tools: {e}")

        for toolkit_name in toolkit_names:
            try:
                toolkit_tools = client.tools.get(
                    user_id=entity_id, toolkits=[toolkit_name]
                )
                tools.extend(toolkit_tools)
            except Exception as e:
                print(
                    f"Warning: Could not load tools for toolkit '{toolkit_name}': {e}"
                )

        return tools
    except Exception as e:
        print(f"Error getting Composio tools: {e}")
        return []


def execute_composio_tool(tool_call, entity_id="default"):

    try:
        client = get_composio_client()

        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)

        result = client.tools.execute(tool_name, user_id=entity_id, arguments=arguments)

        return (
            json.dumps(result)
            if result
            else json.dumps({"error": "No result from Composio"})
        )
    except Exception as e:
        return json.dumps({"error": f"Composio execution error: {str(e)}"})
