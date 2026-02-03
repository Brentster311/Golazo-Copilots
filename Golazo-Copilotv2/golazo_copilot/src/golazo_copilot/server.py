"""Golazo Copilot MCP Server - Entry point for GitHub Copilot integration."""

import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .tools.gcp_init import gcp_init
from .tools.gcp_transition import gcp_transition
from .tools.gcp_mark import gcp_mark_dor, gcp_mark_dod
from .tools.gcp_status import gcp_status

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
        Tool(
            name="gcp_mark_dor",
            description="Mark Definition of Ready items as complete or incomplete",
            inputSchema={
                "type": "object",
                "properties": {
                    "work_item_id": {
                        "type": "string",
                        "description": "Work item identifier"
                    },
                    "item": {
                        "type": "string",
                        "enum": ["userStory", "designDoc", "reviewComments", "testCases"],
                        "description": "Single DoR item to mark"
                    },
                    "items": {
                        "type": "object",
                        "description": "Multiple DoR items to mark (alternative to single item)"
                    },
                    "complete": {
                        "type": "boolean",
                        "default": True,
                        "description": "Whether item is complete"
                    }
                },
                "required": ["work_item_id"]
            }
        ),
        Tool(
            name="gcp_mark_dod",
            description="Mark Definition of Done items as complete or incomplete",
            inputSchema={
                "type": "object",
                "properties": {
                    "work_item_id": {
                        "type": "string",
                        "description": "Work item identifier"
                    },
                    "item": {
                        "type": "string",
                        "enum": ["branchCreated", "testsWrittenFirst", "testsPass",
                                 "buildPasses", "docsUpdated", "refactorComplete", "committed"],
                        "description": "Single DoD item to mark"
                    },
                    "items": {
                        "type": "object",
                        "description": "Multiple DoD items to mark"
                    },
                    "complete": {
                        "type": "boolean",
                        "default": True,
                        "description": "Whether item is complete"
                    }
                },
                "required": ["work_item_id"]
                        }
                    ),
                    Tool(
                        name="gcp_status",
                        description="Get comprehensive workflow status for a work item",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "work_item_id": {
                                    "type": "string",
                                    "description": "Work item identifier"
                                }
                            },
                            "required": ["work_item_id"]
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
    
    elif name == "gcp_mark_dor":
        result = await gcp_mark_dor(
            work_item_id=arguments["work_item_id"],
            item=arguments.get("item"),
            items=arguments.get("items"),
            complete=arguments.get("complete", True)
        )
        
        if result["success"]:
            warning = f"\n?? {result['warning']}" if result.get("warning") else ""
            status = "? Complete" if result["complete"] else f"? Missing: {', '.join(result['missing'])}"
            content = f"""? DoR updated!{warning}

**DoR Status:** {status}

| Item | Status |
|------|--------|
| userStory | {'?' if result['items']['userStory'] else '?'} |
| designDoc | {'?' if result['items']['designDoc'] else '?'} |
| reviewComments | {'?' if result['items']['reviewComments'] else '?'} |
| testCases | {'?' if result['items']['testCases'] else '?'} |
"""
        else:
            content = f"? Failed to update DoR: {result['error']}"
        
        return [TextContent(type="text", text=content)]
    
    elif name == "gcp_mark_dod":
        result = await gcp_mark_dod(
            work_item_id=arguments["work_item_id"],
            item=arguments.get("item"),
            items=arguments.get("items"),
            complete=arguments.get("complete", True)
        )
        
        if result["success"]:
            warning = f"\n?? {result['warning']}" if result.get("warning") else ""
            status = "? Complete" if result["complete"] else f"? Missing: {', '.join(result['missing'])}"
            content = f"""? DoD updated!{warning}

**DoD Status:** {status}
"""
        else:
            content = f"? Failed to update DoD: {result['error']}"
        
        return [TextContent(type="text", text=content)]
    
    elif name == "gcp_status":
        result = await gcp_status(
            work_item_id=arguments["work_item_id"]
        )
        
        if result.get("active", False):
            dor_count = sum(1 for v in result["dor"]["items"].values() if v)
            dor_total = len(result["dor"]["items"])
            dod_count = sum(1 for v in result["dod"]["items"].values() if v)
            dod_total = len(result["dod"]["items"])
            
            dor_status = "? Complete" if result["dor"]["complete"] else f"? {dor_count}/{dor_total}"
            dod_status = "? Complete" if result["dod"]["complete"] else f"? {dod_count}/{dod_total}"
            
            next_steps = "\n".join(f"- {step}" for step in result["next_steps"])
            
            content = f"""**Golazo Status**
- Work Item: {result['work_item_id']}
- Current Role: **{result['current_role']}**
- Phase: {result['current_phase']}
- DoR: {dor_status}
- DoD: {dod_status}

**Next Steps:**
{next_steps}

---
{result['role_instructions']}
"""
        else:
            content = f"?? {result.get('message', 'No active work item')}"
        
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
