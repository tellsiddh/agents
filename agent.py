import json
from client import call_llm
from tools import get_tool_schemas, execute_tool

HANDOFF_PREFIX = "handoff_to_"


class Agent:
    def __init__(
        self, agent_id, system_prompt, tools=None, can_call=None, max_steps=10
    ):
        self.agent_id = agent_id
        self.system_prompt = system_prompt
        self.tool_names = tools or []
        self.can_call = can_call or []
        self.max_steps = max_steps

    def _build_tools(self, agents_map):
        """Build OpenAI-format tool list: internal tools + handoff tools."""
        schemas = get_tool_schemas(self.tool_names)

        for target_id in self.can_call:
            target = agents_map.get(target_id)
            if not target:
                continue
            schemas.append(
                {
                    "type": "function",
                    "function": {
                        "name": f"{HANDOFF_PREFIX}{target_id}",
                        "description": (
                            f"Hand off the task to the '{target_id}' agent. The agent has the following role: "
                            f"{target.system_prompt}"
                        ),
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "message": {
                                    "type": "string",
                                    "description": "The task or question for this agent",
                                }
                            },
                            "required": ["message"],
                        },
                    },
                }
            )

        return schemas or None

    def run(
        self,
        query,
        agents_map,
        model="openai/gpt4o",
        depth=0,
        max_depth=3,
        session_id=None,
        enable_history=False,
    ):
        try:
            print(f"\n[{self.agent_id}] Received query: {query}")
            if depth >= max_depth:
                return f"[{self.agent_id}] Max agent depth ({max_depth}) reached."

            tools = self._build_tools(agents_map)
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": query},
            ]

            for step in range(self.max_steps):
                response = call_llm(
                    messages=messages,
                    model=model,
                    tools=tools,
                    session_id=session_id,
                    enable_history=enable_history,
                )
                msg = response.choices[0].message
                msg_dict = {"role": msg.role, "content": msg.content}
                if msg.tool_calls:
                    msg_dict["tool_calls"] = [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        }
                        for tc in msg.tool_calls
                    ]
                messages.append(msg_dict)

                # No tool calls → final answer
                if not msg.tool_calls:
                    return msg.content

                # Process each tool call
                for tc in msg.tool_calls:
                    name = tc.function.name
                    args = json.loads(tc.function.arguments)

                    if name.startswith(HANDOFF_PREFIX):
                        # ── Handoff to sub-agent ──
                        target_id = name[len(HANDOFF_PREFIX) :]
                        target = agents_map.get(target_id)
                        if target:
                            print(f"  [{self.agent_id}] → handoff to '{target_id}'")
                            result = target.run(
                                query=args["message"],
                                agents_map=agents_map,
                                model=model,
                                depth=depth + 1,
                                max_depth=max_depth,
                                session_id=session_id,
                                enable_history=enable_history,
                            )
                            print(
                                f"  [{self.agent_id}] ← result from '{target_id}': {result}"
                            )
                        else:
                            result = f"Agent '{target_id}' not found."
                    else:
                        print(
                            f"  [{self.agent_id}] → executing tool '{name}' with args={args}"
                        )
                        # ── Internal tool call ──
                        print(f"  [{self.agent_id}] → tool '{name}' args={args}")
                        result = execute_tool(name, args)

                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "content": str(result),
                        }
                    )

            return f"[{self.agent_id}] Max steps ({self.max_steps}) reached."
        except Exception as e:
            return f"[{self.agent_id}] Error: {str(e)}"
