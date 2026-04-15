# demo client to test MCP server functionality
import asyncio
from fastmcp import Client

client = Client("http://localhost:8000/mcp")


async def call_tool(a: int, b: int):
    async with client:
        result = await client.call_tool("add", {"a": a, "b": b})
        print(result)


asyncio.run(call_tool(3, 5))


# list all tools in the MCP server
async def list_tools():
    async with client:
        tools = await client.list_tools()
        for t in tools:
            print(f"Tool: {t.name}, Description: {t.description}")


asyncio.run(list_tools())


async def call_nonexistent_tool():
    async with client:
        try:
            result = await client.call_tool("nonexistent_tool", {"x": 1})
            print(result)
        except Exception as e:
            print(f"Error calling nonexistent tool: {e}")


asyncio.run(call_nonexistent_tool())
