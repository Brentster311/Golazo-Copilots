"""Run an MCP stdio exchange against an installed Golazo wheel."""

import asyncio
import sys
from importlib.metadata import version

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

EXPECTED_TOOLS = {
    "golazo_bootstrap",
    "golazo_capabilities",
    "golazo_consent",
    "golazo_create_workitem",
    "golazo_git_propose",
    "golazo_role_context",
    "golazo_status",
    "golazo_transition",
    "golazo_transition_workitem",
}


async def main(workspace_path: str) -> None:
    stage = "startup"
    try:
        parameters = StdioServerParameters(
            command=sys.executable,
            args=["-m", "golazo_copilot.server"],
        )
        async with stdio_client(parameters) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                stage = "initialize"
                await session.initialize()
                stage = "list"
                listed = await session.list_tools()
                assert {tool.name for tool in listed.tools} == EXPECTED_TOOLS
                stage = "call"
                result = await session.call_tool(
                    "golazo_status",
                    {"workspace_path": workspace_path},
                )
                assert result.is_error is False
                assert result.content[0].text.startswith("**Golazo Copilot**")
        print(
            f"PASS golazo-copilot={version('golazo-copilot')} "
            f"mcp={version('mcp')} stage=shutdown"
        )
    except Exception as exc:
        print(
            f"FAIL golazo-copilot={version('golazo-copilot')} "
            f"mcp={version('mcp')} stage={stage} exception={type(exc).__name__}",
            file=sys.stderr,
        )
        raise


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1]))