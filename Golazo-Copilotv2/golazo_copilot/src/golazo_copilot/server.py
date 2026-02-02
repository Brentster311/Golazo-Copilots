"""Golazo Copilot MCP Server - Entry point for GitHub Copilot integration."""

import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .tools.gcp_init import gcp_init
from .tools.gcp_transition import gcp_transition

# Create server instance
server = Server("golazo-copilot")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="gcp_init",
            description="Initialize a new Golazo Copilot work item with persistent state tracking",
            inputSchema={
                "type": "object",
                "properties": {
                    "work_item_id": {
                        "type": "string",
                        "description": "Unique identifier for the work item (alphanumeric, hyphens, underscores)"
                    },
                    "profile": {
                        "type": "string",
                        "enum": ["complete", "express", "spike"],
                        "default": "complete",
                        "description": "Workflow profile determining which gates are enforced"
                    }
                },
                "required": ["work_item_id"]
            }
        ),
        Tool(
            name="gcp_transition",
            description="Transition to a new role in the Golazo Copilot workflow",
            inputSchema={
                "type": "object",
                "properties": {
                    "work_item_id": {
                        "type": "string",
                        "description": "Work item identifier"
                    },
                    "role": {
                        "type": "string",
                        "enum": ["project-owner", "program-manager", "quality-assurance",
                                 "architect", "developer", "refactor-expert", "builder", "documentor"],
                        "description": "Target role to transition to"
                    },
                    "force": {
                        "type": "boolean",
                        "default": False,
                        "description": "Force transition even if gates not met (requires prior consent)"
                    }
                },
                "required": ["work_item_id", "role"]
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    if name == "gcp_init":
        result = await gcp_init(
            work_item_id=arguments["work_item_id"],
            profile=arguments.get("profile", "complete")
        )
        
        if result["success"]:
            content = f"""? Work item '{result['work_item_id']}' initialized!

**Current Role:** {result['current_role']}

---
{result['role_instructions']}
"""
        else:
            content = f"? Failed to initialize: {result['error']}"
        
        return [TextContent(type="text", text=content)]
    
    elif name == "gcp_transition":
        result = await gcp_transition(
            work_item_id=arguments["work_item_id"],
            role=arguments["role"],
            force=arguments.get("force", False)
        )
        
        if result["success"]:
            warning = f"\n?? {result['warning']}" if result.get("warning") else ""
            content = f"""? Transitioned to '{result['current_role']}'!{warning}

**Current Phase:** {result['current_phase']}

---
{result['role_instructions']}
"""
        else:
            missing = ""
            if result.get("missing"):
                missing = f"\n\n**Missing DoR items:** {', '.join(result['missing'])}"
            content = f"? Transition failed: {result['error']}{missing}"
        
        return [TextContent(type="text", text=content)]
    
    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def run():
    """Entry point for the server."""
    asyncio.run(main())


if __name__ == "__main__":
    run()
