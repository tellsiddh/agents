# Tools Directory

This directory contains the modular tool system for the multi-agent framework.

## Structure

```
tools/
├── __init__.py           # Package exports
├── internal_tools.py     # Built-in Python functions
├── composio_tools.py     # Composio authenticated integrations
├── mcp_tools.py          # Model Context Protocol (future)
└── README.md             # This file
```

## Tool Types

### 1. Internal Tools (`internal_tools.py`)

Built-in Python functions that don't require external authentication:

- `get_weather` - Mock weather API
- `calculate` - Math expression evaluator
- `convert_units` - Temperature, distance, weight conversions
- `get_time` - Current time with timezone support
- `search_knowledge` - Internal knowledge base search
- `list_files` - Directory listing

**Usage in config.json:**
```json
{
  "tools": ["get_weather", "calculate"],
  "auth_ref": "internal"
}
```

### 2. Composio Tools (`composio_tools.py`)

External integrations through Composio (Gmail, Slack, etc.) that require user authentication.

**Two ways to specify Composio tools:**

#### Option A: Specify App Name (Recommended)
Agent gets ALL actions for that app and picks the right one:

```json
{
  "tools": ["GMAIL", "SLACK"],
  "name": "GMAIL",
  "auth_ref": "composio"
}
```

When you specify `"GMAIL"`, the agent receives all Gmail actions:
- `GMAIL_SEND_EMAIL`
- `GMAIL_FETCH_EMAILS`
- `GMAIL_SEARCH_EMAILS`
- `GMAIL_CREATE_DRAFT`
- etc.

The LLM automatically picks the appropriate action based on the user's request.

#### Option B: Specify Specific Actions
For fine-grained control:

```json
{
  "tools": ["GMAIL_SEND_EMAIL", "GMAIL_FETCH_EMAILS"],
  "name": "GMAIL_SEND_EMAIL",
  "auth_ref": "composio"
}
```

**Available Composio Apps:**
- `GMAIL` - Email management
- `SLACK` - Team communication
- `GITHUB` - Repository management
- `CALENDAR` - Google Calendar
- `DRIVE` - Google Drive
- Many more... (see Composio docs)

**Authentication:**

1. Add Composio API key to `.env`:
   ```bash
   COMPOSIO_API_KEY=your_composio_api_key
   ```

2. Set `entity_id` in config.json (user identifier):
   ```json
   {
     "entity_id": "user@example.com"
   }
   ```

3. User must authenticate with the app (Gmail, Slack, etc.) through Composio's OAuth flow

### 3. MCP Tools (`mcp_tools.py`)

Model Context Protocol integration (coming soon).

Will support:
- Database connections
- Custom API servers
- File system access
- External knowledge bases

## Adding New Tools

### Adding an Internal Tool

1. Open `internal_tools.py`
2. Use the `@tool` decorator:

```python
@tool(
    "my_tool",
    "Description of what the tool does",
    {
        "type": "object",
        "properties": {
            "param": {"type": "string", "description": "Parameter description"}
        },
        "required": ["param"]
    }
)
def my_tool(param: str):
    # Implementation
    return {"result": "value"}
```

3. Add to agent's tools in `config.json`:
```json
{
  "agent_id": "main",
  "tools": ["my_tool"]
}
```

4. Add to tools registry:
```json
{
  "tools": [
    { "name": "my_tool", "auth_ref": "internal" }
  ]
}
```

### Adding a Composio Integration

1. Find the app name in [Composio Apps](https://docs.composio.dev/apps)
2. Add to agent's tools in `config.json`:
```json
{
  "agent_id": "main",
  "tools": ["APPNAME"]
}
```

3. Add to tools registry:
```json
{
  "tools": [
    { "name": "APPNAME", "auth_ref": "composio", "description": "App description" }
  ]
}
```

4. Ensure user authenticates with the app through Composio

## Examples

### Example 1: Agent with Internal and Composio Tools

```json
{
  "agent_id": "assistant",
  "system_prompt": "You help with emails and calculations",
  "tools": [
    "calculate",
    "get_time",
    "GMAIL"
  ],
  "tools_config": [
    { "name": "calculate", "auth_ref": "internal" },
    { "name": "get_time", "auth_ref": "internal" },
    { "name": "GMAIL", "auth_ref": "composio" }
  ]
}
```

User query: *"Send an email to john@example.com with today's date"*

Agent execution:
1. Calls `get_time()` → Gets current date
2. Calls `GMAIL_SEND_EMAIL` (picked from GMAIL actions) → Sends email

### Example 2: Multiple Composio Apps

```json
{
  "tools": ["GMAIL", "SLACK", "CALENDAR"],
  "tools_config": [
    { "name": "GMAIL", "auth_ref": "composio" },
    { "name": "SLACK", "auth_ref": "composio" },
    { "name": "CALENDAR", "auth_ref": "composio" }
  ]
}
```

User query: *"Check my calendar for tomorrow and send a Slack message to #team with my schedule"*

Agent execution:
1. Calls `CALENDAR_FETCH_EVENTS` → Gets tomorrow's events
2. Calls `SLACK_SEND_MESSAGE` → Posts to channel

## Technical Details

### Tool Resolution Flow

```
Agent receives query
    ↓
Agent.run() calls _build_tools()
    ↓
_build_tools() calls:
    - get_tool_schemas() for internal tools
    - get_composio_tools() for Composio tools
    ↓
LLM receives combined tool list
    ↓
LLM picks tools and generates tool_calls
    ↓
Agent executes:
    - execute_tool() for internal
    - execute_composio_tool() for Composio
    ↓
Results added to conversation
    ↓
Repeat until final answer
```

### Entity ID (User Authentication)

The `entity_id` in config.json identifies the user for Composio authentication:
- Each user has unique connected accounts
- Same agent can work for different users
- Composio manages OAuth tokens per entity

```python
result = agent.run(
    query="Send email",
    entity_id="user@example.com",  # This user's Gmail
    ...
)
```

## Debugging

### Check Available Tools

```python
from tools import TOOL_REGISTRY, get_available_composio_actions

# List internal tools
print("Internal:", list(TOOL_REGISTRY.keys()))

# List Composio actions
print("Composio:", get_available_composio_actions()[:10])
```

### Test Tool Execution

```python
from tools import execute_tool, get_composio_tools

# Test internal tool
result = execute_tool("calculate", {"expression": "2+2"})
print(result)

# Test Composio tool loading
tools = get_composio_tools(["GMAIL"], entity_id="test@example.com")
print(f"Loaded {len(tools)} Gmail tools")
```

## Best Practices

1. **Use app names for Composio** - Let the agent pick specific actions
2. **Keep internal tools focused** - One tool, one purpose
3. **Document tool parameters** - Clear descriptions help the LLM
4. **Handle errors gracefully** - Return error objects, don't raise exceptions
5. **Test tools independently** - Before adding to agents

## Future Enhancements

- [ ] MCP server integration
- [ ] Tool usage analytics
- [ ] Custom tool marketplace
- [ ] Tool composition (chain tools)
- [ ] Tool rate limiting
- [ ] Tool cost tracking
