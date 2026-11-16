"""Starts the MCP servers listed in mcp.json and routes tool calls to them."""

import asyncio
import json
from pathlib import Path

from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parent


async def ask_approval(context, params):
    """Answers a server's approval request with a y/N prompt in this terminal."""
    print(f"\n{params.message}")
    answer = await asyncio.to_thread(input, "Run this tool? [y/N]: ")
    return types.ElicitResult(action="accept", content={"approve": answer.strip().lower() == "y"})


class MCPClient:
    def __init__(self):
        self.sessions = {}  # tool name -> session of the server that owns it
        self.tool_list = []  # (name, description, example args) for the prompt
        self.instructions = []

    async def connect(self, stack):
        servers = json.loads((ROOT / "mcp.json").read_text())["mcpServers"]
        for server_name, spec in servers.items():
            params = StdioServerParameters(
                command=str(ROOT / spec["command"]), args=spec.get("args", []), cwd=ROOT
            )
            read_stream, write_stream = await stack.enter_async_context(stdio_client(params))
            session = await stack.enter_async_context(
                ClientSession(read_stream, write_stream, elicitation_callback=ask_approval)
            )
            info = await session.initialize()
            if info.instructions:
                self.instructions.append(info.instructions)

            server_tools = (await session.list_tools()).tools
            print(f"MCP server '{server_name}': {', '.join(tool.name for tool in server_tools)}")
            for tool in server_tools:
                properties = tool.inputSchema.get("properties", {})
                args = {key: prop.get("examples", ["..."])[0] for key, prop in properties.items()}
                self.sessions[tool.name] = session
                self.tool_list.append((tool.name, tool.description, args))
        return self

    async def call_tool(self, name, args):
        """Sends one tool call to the MCP server that owns the tool."""
        if not isinstance(name, str) or name not in self.sessions:
            return {"error": f"Unknown tool; use {', '.join(self.sessions)}"}
        if not isinstance(args, dict):
            return {"error": "args must be a JSON object"}
        result = await self.sessions[name].call_tool(name, args)
        if result.structuredContent is not None and not result.isError:
            return result.structuredContent
        text = "\n".join(block.text for block in result.content if block.type == "text")
        return {"error": text} if result.isError else {"content": text}
