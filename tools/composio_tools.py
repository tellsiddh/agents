import json
from dotenv import load_dotenv

load_dotenv()

try:
    from composio_openai import ComposioToolSet, Action

    COMPOSIO_AVAILABLE = True
except ImportError:
    COMPOSIO_AVAILABLE = False
    ComposioToolSet = None
    Action = None

COMPOSIO_TOOLSET = None


def get_composio_toolset(entity_id="default"):
    if not COMPOSIO_AVAILABLE:
        raise ImportError(
            "composio-openai not installed. Run: pip install composio-openai"
        )
    global COMPOSIO_TOOLSET
    if COMPOSIO_TOOLSET is None:
        COMPOSIO_TOOLSET = ComposioToolSet(entity_id=entity_id)
    return COMPOSIO_TOOLSET


def get_composio_tools(actions, entity_id="default"):
    if not COMPOSIO_AVAILABLE:
        print("Warning: composio-openai not installed. Skipping Composio tools.")
        return []

    try:
        toolset = get_composio_toolset(entity_id)
        tools = []

        for action_name in actions:
            if "_" in action_name:
                try:
                    tools.extend(
                        toolset.get_tools(actions=[getattr(Action, action_name)])
                    )
                except AttributeError:
                    print(f"Warning: Composio action '{action_name}' not found")
            else:
                try:
                    app_tools = toolset.get_tools(apps=[action_name])
                    tools.extend(app_tools)
                    print(f"Loaded {len(app_tools)} tools for {action_name}")
                except Exception as e:
                    print(f"Warning: Could not load tools for app '{action_name}': {e}")

        return tools
    except Exception as e:
        print(f"Error getting Composio tools: {e}")
        return []


def execute_composio_tool(tool_call, entity_id="default"):
    if not COMPOSIO_AVAILABLE:
        return json.dumps({"error": "composio-openai not installed"})

    try:
        toolset = get_composio_toolset(entity_id)
        result = toolset.handle_tool_calls([tool_call])
        return (
            json.dumps(result[0])
            if result
            else json.dumps({"error": "No result from Composio"})
        )
    except Exception as e:
        return json.dumps({"error": f"Composio execution error: {str(e)}"})


def get_available_composio_actions():
    if not COMPOSIO_AVAILABLE:
        return []
    try:
        return [
            attr for attr in dir(Action) if not attr.startswith("_") and attr.isupper()
        ]
    except Exception as e:
        print(f"Error getting Composio actions: {e}")
        return []
