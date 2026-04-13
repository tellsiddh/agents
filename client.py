from openai import OpenAI
from dotenv import load_dotenv
import os
import httpx

load_dotenv()

_client = OpenAI(
    base_url=os.getenv("CREATEAI_API_URL"),
    api_key=os.getenv("CREATEAI_API_KEY"),
    http_client=httpx.Client(verify=False),
)


def call_llm(
    messages: list,
    model: str,
    tools: list = None,
    session_id: str = None,
    enable_history: bool = False,
):
    """Send messages to the LLM and return the raw response."""
    print(f"\n[LLM] Calling model '{model}' with messages:")
    agents_metadata = {
        "agent_id": "agent",
        "agent_name": "agent",
        "agent_uuid": "user-uuid",
    }
    extra_body = {
        "session_id": session_id,
        "enable_history": enable_history,
        "agents_metadata": agents_metadata,
    }
    print("extra_body:", extra_body)
    extra_body = {k: v for k, v in extra_body.items() if v is not None} or None
    return _client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools if tools else None,
        extra_body=extra_body,
    )
