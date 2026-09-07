"""GCP-0073 tests for the MCP SDK 2.x server migration."""

import sys
from importlib.metadata import version
from pathlib import Path

import pytest

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.types import CallToolRequestParams, CallToolResult, ListToolsResult

from golazo_copilot import server
from golazo_copilot.dispatch.registry import get_tool_definitions


@pytest.mark.asyncio
async def test_mcp2_list_handler_preserves_registry_contract():
    result = await server.handle_list_tools(None, None)

    assert isinstance(result, ListToolsResult)
    assert result.tools == get_tool_definitions()
    assert all(tool.input_schema.get("type") == "object" for tool in result.tools)


@pytest.mark.asyncio
async def test_mcp2_call_handler_normalizes_omitted_arguments():
    params = CallToolRequestParams(name="does_not_exist", arguments=None)

    result = await server.handle_call_tool(None, params)

    assert isinstance(result, CallToolResult)
    assert result.is_error is True
    assert result.content[0].text == "Unknown tool: does_not_exist"


@pytest.mark.asyncio
async def test_mcp2_call_handler_preserves_recoverable_error_text():
    params = CallToolRequestParams(name="golazo_bootstrap", arguments={})

    result = await server.handle_call_tool(None, params)

    assert result.is_error is True
    assert result.content[0].text == "[FAIL] workspace_path is required"


def test_mcp2_handlers_are_registered_by_method():
    assert server.server.get_request_handler("tools/list") is not None
    assert server.server.get_request_handler("tools/call") is not None


def test_mcp_dependency_is_bounded_to_major_version_2():
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    project = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))["project"]

    assert "mcp>=2,<3" in project["dependencies"]
    assert not any(dependency.startswith("mcp-types") for dependency in project["dependencies"])


@pytest.mark.asyncio
async def test_mcp2_stdio_initialize_list_and_call(tmp_path):
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
                assert {tool.name for tool in listed.tools} == {
                    tool.name for tool in get_tool_definitions()
                }
                stage = "call"
                result = await session.call_tool(
                    "golazo_status",
                    {"workspace_path": str(tmp_path)},
                )
                assert result.is_error is False
                assert result.content[0].text.startswith("**Golazo Copilot**")
    except Exception as exc:
        pytest.fail(
            f"stdio stage={stage}; golazo-copilot={version('golazo-copilot')}; "
            f"mcp={version('mcp')}; exception={type(exc).__name__}"
        )