"""MCP server that exposes the harness tools from tools.py over stdio."""

import asyncio

from mcp import types
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server

import tools

server = Server("mini-harness-tools", instructions=tools.GUIDANCE)

APPROVAL_SCHEMA = {
    "type": "object",
    "properties": {"approve": {"type": "boolean", "title": "Run this tool?"}},
    "required": ["approve"],
}


async def ask_approval(name, args):
    # The server has no terminal, so it asks the client to ask the user (MCP elicitation).
    context = server.request_context
    result = await context.session.elicit(
        tools.approval_message(name, args),
        APPROVAL_SCHEMA,
        related_request_id=context.request_id,
    )
    return result.action == "accept" and bool((result.content or {}).get("approve"))


@server.list_tools()
async def list_tools():
    return [
        types.Tool(
            name=name,
            description=tool["description"],
            inputSchema={
                "type": "object",
                "properties": {
                    key: {"type": "string", "examples": [example]}
                    for key, example in tool["args"].items()
                },
                "required": list(tool["args"]),
            },
            outputSchema={"type": "object"},
        )
        for name, tool in tools.TOOLS.items()
    ]


@server.call_tool()
async def call_tool(name, args):
    error = tools.check_call(name, args)
    if error:
        return {"error": error}
    if tools.TOOLS[name]["approval"] and not await ask_approval(name, args):
        return {"cancelled": "User declined this tool"}
    return await asyncio.to_thread(tools.execute, name, args)


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
