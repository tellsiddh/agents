# Multi-Agent Orchestration System

A powerful, flexible multi-agent system that enables complex task decomposition and execution through hierarchical agent collaboration. Built on a unified tool abstraction where everything—from simple functions to API calls to other agents—is treated as a tool.

## Core Concept

**Everything is a tool.** Whether it's a function, an API call, an MCP server, or even another agent—the orchestrator treats all capabilities uniformly. This design enables:

- **Recursive Agent Calls**: Agents can delegate tasks to other specialized agents
- **Hierarchical Task Decomposition**: Complex queries are broken down into manageable subtasks
- **Flexible Tool Integration**: Seamlessly mix internal tools, external APIs, and sub-agents
- **Cycle Detection**: Prevents infinite loops with configurable max depth and cycle detection

## Architecture Overview

The system follows a hierarchical orchestration pattern:

```
User Query → Main Agent → [Tools | Sub-Agents | MCP Servers]
                              ↓           ↓
                         Direct      Sub-Agent → [Their Tools | Other Sub-Agents]
                        Execution        ↓
                                    Synthesized Results → Main Agent → Final Response
```

### Key Design Principles

1. **Agent Handoff Protocol**: Agents can hand off tasks to specialized agents using `handoff_to_<agent_id>` functions
2. **Execution Context Tracking**: Each call maintains `call_chain` and `depth` to prevent cycles
3. **Iterative Refinement**: Agents can make multiple tool calls in a loop until they have sufficient information
4. **Configurable Depth**: `max_depth` parameter prevents runaway recursive calls

See the detailed architecture diagram: [assets/agent_architecture.svg](assets/agent_architecture.svg)

## Project Structure

```
agents/
├── agent.py              # Core Agent class with handoff logic
├── client.py             # LLM client wrapper (OpenAI-compatible)
├── tools.py              # Tool registry and built-in tools
├── main.py               # Entry point and agent orchestration
├── config.json           # Agent definitions and project configuration
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (API keys)
├── LICENSE               # GNU GPL v3
└── assets/
    └── agent_architecture.txt  # System architecture diagram
```

## Core Components

### 1. Agent Class ([agent.py](agent.py))

The `Agent` class is the heart of the system. Each agent has:

- **Identity**: `agent_id` and `system_prompt` defining its role
- **Capabilities**: `tool_names` list of tools it can use
- **Delegation**: `can_call` list of agent IDs it can hand off to
- **Limits**: `max_steps` for iterative loops

**Key Methods:**
- `_build_tools()`: Dynamically constructs tool schemas including handoff functions
- `run()`: Main execution loop with depth tracking and cycle prevention

**Handoff Mechanism:**
When an agent calls `handoff_to_<agent_id>`, the system:
1. Identifies the target agent
2. Executes `target.run()` with incremented depth
3. Returns the result to the calling agent
4. Continues the calling agent's execution

### 2. Tool System ([tools.py](tools.py))

**Tool Registry Pattern:**
- Decorator-based registration: `@tool(name, description, parameters)`
- OpenAI function calling schema generation
- Centralized execution with error handling

**Built-in Tools:**

| Tool | Purpose | Parameters |
|------|---------|------------|
| `get_weather` | Retrieve weather data for a location | `location: str` |
| `calculate` | Evaluate math expressions | `expression: str` |
| `convert_units` | Convert between units (temp, distance, weight) | `value: float, from_unit: str, to_unit: str` |
| `search_knowledge` | Search internal knowledge base | `query: str, max_results: int` |
| `get_time` | Get current time with timezone offset | `utc_offset: float` |
| `list_files` | List files in a directory | `path: str` |

**Adding New Tools:**
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

### 3. LLM Client ([client.py](client.py))

Wrapper around OpenAI's API with:
- Environment variable configuration
- Session management for conversation history
- Agent metadata tracking
- SSL verification bypass for internal APIs
- Support for custom base URLs

**Configuration:**
```python
base_url = os.getenv("CREATEAI_API_URL")
api_key = os.getenv("CREATEAI_API_KEY")
```

### 4. Main Orchestrator ([main.py](main.py))

Entry point that:
1. Loads configuration from `config.json`
2. Builds agent instances with their capabilities
3. Executes the main agent with user query
4. Handles session history if enabled

**Query Execution Flow:**
```
read_config() → build_agents() → main_agent.run() → print result
```

## Configuration ([config.json](config.json))

### Agent Definition

```json
{
  "agent_id": "main",
  "role": "main",
  "system_prompt": "You are the main agent...",
  "can_call": ["research_agent", "math_agent"],
  "tools": ["get_weather", "get_time"],
  "max_steps": 20
}
```

**Fields:**
- `agent_id`: Unique identifier
- `role`: "main" or "sub_agent"
- `system_prompt`: Instructions defining the agent's behavior
- `can_call`: List of agent_ids this agent can hand off to
- `tools`: List of tool names this agent can use
- `max_steps`: Maximum iterations in the execution loop

### Project Settings

```json
{
  "session_id": "unique_session",
  "agent_settings": {
    "max_depth": 3,
    "timeout_ms": 30000,
    "cycle_detection": true
  }
}
```

### Example Agent Hierarchy

**Current Configuration:**

```
main_agent (orchestrator)
├── Tools: get_weather, get_time, convert_units, list_files
└── Can call:
    ├── research_agent
    │   └── Tools: search_knowledge
    ├── math_agent
    │   └── Tools: calculate, convert_units
    └── creative_agent
        └── Tools: (uses LLM directly for creative tasks)
```

## Getting Started

### Prerequisites

- Python 3.10+
- OpenAI-compatible API endpoint

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd agents
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   
   Create a `.env` file in the project root:
   ```bash
   CREATEAI_API_KEY=your_api_key_here
   CREATEAI_API_URL=https://your-api-endpoint.com
   ```

4. **Run the system**
   ```bash
   python main.py
   ```

## Usage Examples

### Example 1: Multi-Step Query with Agent Handoffs

```python
query = (
    "I need help with a few things: "
    "1) What's the weather in Tokyo and convert the temperature to Celsius, "
    "2) Calculate the compound interest on $10,000 at 5% annual rate for 3 years, "
    "3) Find me some info about machine learning, "
    "4) Write me a short haiku inspired by the weather in Tokyo."
)

result = agents["main"].run(
    query=query,
    agents_map=agents,
    model="openai/gpt4o_mini",
    max_depth=3,
    session_id="example_session",
    enable_history=True
)
```

**Execution Flow:**
1. Main agent receives complex query
2. Calls `get_weather` tool for Tokyo
3. Calls `convert_units` to convert F→C
4. Hands off to `research_agent` for ML info
5. Hands off to `math_agent` for compound interest
6. Hands off to `creative_agent` for haiku
7. Synthesizes all results into final response

### Example 2: Simple Tool Usage

```python
query = "What is 55kg in lb?"

result = agents["main"].run(
    query=query,
    agents_map=agents,
    model="openai/gpt4o_mini"
)
```

**Execution Flow:**
1. Main agent identifies unit conversion task
2. Hands off to `math_agent`
3. Math agent calls `convert_units(55, "kg", "lb")`
4. Returns `121.25 lb`

### Example 3: Debugging Agent Execution

Enable detailed logging to see the agent decision-making process:

```python
# In agent.py, the system prints:
# - Agent ID and received query
# - Handoff decisions: "[agent_id] → handoff to 'target_id'"
# - Tool executions: "[agent_id] → tool 'tool_name' args={...}"
# - Results: "[agent_id] ← result from 'target_id': ..."
```

## How Agents Work

### Agent Execution Loop

```python
for step in range(max_steps):
    1. Call LLM with current messages + available tools
    2. Receive response (may include tool_calls)
    3. If no tool_calls → return final answer
    4. For each tool_call:
       a. If handoff → call sub-agent
       b. If tool → execute tool
       c. Append result to messages
    5. Continue loop
```

### Depth and Cycle Protection

- **depth**: Incremented on each agent handoff
- **max_depth**: Hard limit (default: 3)
- **call_chain**: Tracks sequence of agent IDs
- **cycle_detection**: Prevents agent from calling parent

### Message History

The system maintains OpenAI-style message history:
```python
messages = [
    {"role": "system", "content": "You are..."},
    {"role": "user", "content": "User query"},
    {"role": "assistant", "content": "...", "tool_calls": [...]},
    {"role": "tool", "tool_call_id": "...", "content": "result"}
]
```

## 🛠️ Extending the System

### Adding a New Agent

1. **Define in config.json:**
   ```json
   {
     "agent_id": "data_agent",
     "role": "sub_agent",
     "system_prompt": "You are a data analysis specialist...",
     "can_call": [],
     "tools": ["calculate", "list_files"],
     "max_steps": 10
   }
   ```

2. **Add to parent's can_call:**
   ```json
   {
     "agent_id": "main",
     "can_call": ["research_agent", "math_agent", "data_agent"]
   }
   ```

### Adding External API Tools

```python
@tool(
    "call_external_api",
    "Call an external REST API",
    {
        "type": "object",
        "properties": {
            "endpoint": {"type": "string"},
            "method": {"type": "string"},
            "data": {"type": "object"}
        }
    }
)
def call_external_api(endpoint: str, method: str = "GET", data: dict = None):
    import requests
    response = requests.request(method, endpoint, json=data)
    return response.json()
```

### Integrating MCP Servers

The system supports Model Context Protocol (MCP) servers. To add:

1. Update `config.json`:
   ```json
   {
     "tools": [
       {
         "name": "mcp_tool",
         "auth_ref": "mcp_api_key",
         "base_url": "https://mcp-server.com"
       }
     ]
   }
   ```

2. Implement MCP client in `tools.py`

## Example Output

```
[main] Received query: I need help with a few things: 1) What's the weather...

[main] → executing tool 'get_weather' with args={'location': 'Tokyo'}
[main] → handoff to 'math_agent'

[math_agent] Received query: Calculate compound interest on $10,000 at 5%...
[math_agent] → tool 'calculate' args={'expression': '10000 * (1 + 0.05)**3'}
[main] ← result from 'math_agent': The compound interest is $11,576.25

[main] → handoff to 'research_agent'
[research_agent] Received query: Find info about machine learning
[research_agent] → tool 'search_knowledge' args={'query': 'machine learning'}
[main] ← result from 'research_agent': Machine learning involves...

[main] → handoff to 'creative_agent'
[creative_agent] Received query: Write a haiku about Tokyo weather...
[main] ← result from 'creative_agent': Cloudy Tokyo skies...

=== Final Answer ===
Here's everything you requested:

1. **Tokyo Weather**: Currently 58°F (14.4°C), cloudy with 65% humidity
2. **Compound Interest**: $11,576.25 after 3 years
3. **Machine Learning**: Involves supervised and unsupervised learning...
4. **Haiku**:
   Cloudy Tokyo skies
   Fourteen degrees, misty air
   Gentle wind whispers
```

## Testing

Run unit tests for individual components:

```bash
# Test tools
python -c "from tools import calculate, convert_units, get_weather; \
  print(calculate('2+2')); \
  print(convert_units(100, 'F', 'C')); \
  print(get_weather('Tokyo'))"

# Test agent initialization
python -c "from main import read_config, build_agents; \
  config = read_config('config.json'); \
  agents = build_agents(config); \
  print(list(agents.keys()))"
```

## License

This project is licensed under the GNU General Public License v3.0. See [LICENSE](LICENSE) for details.

## TODO

- [ ] Add composio tool support
- [ ] Add MCP Support
- [ ] Add Knowledge Base Tools

Architecture Diagram: [assets/agent_architecture.svg](assets/agent_architecture.svg)
