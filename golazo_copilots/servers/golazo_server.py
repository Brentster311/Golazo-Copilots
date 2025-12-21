"""MCP server for Golazo workflow management."""

import json
from typing import Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent, EmbeddedResource
from pydantic import AnyUrl

from golazo_copilots.models import (
    Ticket,
    DesignDoc,
    TicketPriority,
    TicketStatus,
    WorkflowState,
)
from golazo_copilots.orchestrator.workflow_manager import WorkflowManager


class GolazoMCPServer:
    """MCP Server implementing Golazo workflow capabilities."""

    def __init__(self) -> None:
        self.server = Server("golazo-server")
        self.workflow_manager = WorkflowManager()
        self._register_handlers()

    def _register_handlers(self) -> None:
        """Register all MCP protocol handlers."""
        
        @self.server.list_resources()
        async def list_resources() -> list[Resource]:
            """List available workflow resources."""
            return [
                Resource(
                    uri=AnyUrl("golazo://workflow/state"),
                    name="Workflow State",
                    mimeType="application/json",
                    description="Current state of the workflow board",
                ),
                Resource(
                    uri=AnyUrl("golazo://workflow/tickets"),
                    name="All Tickets",
                    mimeType="application/json",
                    description="All tickets in the system",
                ),
                Resource(
                    uri=AnyUrl("golazo://workflow/wip"),
                    name="Work In Progress",
                    mimeType="application/json",
                    description="Current WIP status and limits",
                ),
            ]

        @self.server.read_resource()
        async def read_resource(uri: AnyUrl) -> str:
            """Read a workflow resource."""
            uri_str = str(uri)
            
            if uri_str == "golazo://workflow/state":
                state = self.workflow_manager.get_workflow_state()
                return state.model_dump_json(indent=2)
            
            elif uri_str == "golazo://workflow/tickets":
                tickets = self.workflow_manager.list_tickets()
                return json.dumps([t.model_dump() for t in tickets], indent=2, default=str)
            
            elif uri_str == "golazo://workflow/wip":
                wip_status = self.workflow_manager.get_wip_status()
                return json.dumps(wip_status, indent=2)
            
            else:
                raise ValueError(f"Unknown resource: {uri}")

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available Golazo workflow tools."""
            return [
                Tool(
                    name="create_ticket",
                    description="Create a new work ticket in the Golazo workflow",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "priority": {
                                "type": "string",
                                "enum": ["swarm", "interrupt", "planned"],
                            },
                            "created_by": {"type": "string"},
                            "estimated_days": {"type": "number"},
                        },
                        "required": ["title", "description", "priority", "created_by"],
                    },
                ),
                Tool(
                    name="create_design_doc",
                    description="Create a design document for a ticket",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "ticket_id": {"type": "string"},
                            "title": {"type": "string"},
                            "problem_statement": {"type": "string"},
                            "proposed_solution": {"type": "string"},
                            "success_criteria": {"type": "string"},
                            "author": {"type": "string"},
                            "alternatives_considered": {"type": "string"},
                            "risks": {"type": "string"},
                        },
                        "required": [
                            "ticket_id",
                            "title",
                            "problem_statement",
                            "proposed_solution",
                            "success_criteria",
                            "author",
                        ],
                    },
                ),
                Tool(
                    name="approve_design",
                    description="Approve a design document (requires 2 approvals)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "ticket_id": {"type": "string"},
                            "approver": {"type": "string"},
                        },
                        "required": ["ticket_id", "approver"],
                    },
                ),
                Tool(
                    name="start_work",
                    description="Start working on a ticket (checks WIP limits)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "ticket_id": {"type": "string"},
                            "assignee": {"type": "string"},
                        },
                        "required": ["ticket_id", "assignee"],
                    },
                ),
                Tool(
                    name="submit_for_review",
                    description="Submit work for code review",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "ticket_id": {"type": "string"},
                            "pr_url": {"type": "string"},
                        },
                        "required": ["ticket_id", "pr_url"],
                    },
                ),
                Tool(
                    name="complete_validation",
                    description="Complete customer validation and mark ticket as done",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "ticket_id": {"type": "string"},
                            "validation_notes": {"type": "string"},
                        },
                        "required": ["ticket_id", "validation_notes"],
                    },
                ),
                Tool(
                    name="get_ready_tickets",
                    description="Get all tickets ready to be picked up",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    },
                ),
                Tool(
                    name="update_wip_limit",
                    description="Update the WIP (Work In Progress) limit",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "limit": {"type": "integer", "minimum": 1},
                        },
                        "required": ["limit"],
                    },
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            """Execute a Golazo workflow tool."""
            
            if name == "create_ticket":
                ticket = self.workflow_manager.create_ticket(
                    title=arguments["title"],
                    description=arguments["description"],
                    priority=TicketPriority(arguments["priority"]),
                    created_by=arguments["created_by"],
                    estimated_days=arguments.get("estimated_days"),
                )
                return [
                    TextContent(
                        type="text",
                        text=f"Created ticket {ticket.id}: {ticket.title}",
                    )
                ]
            
            elif name == "create_design_doc":
                design_doc = self.workflow_manager.create_design_doc(
                    ticket_id=arguments["ticket_id"],
                    title=arguments["title"],
                    problem_statement=arguments["problem_statement"],
                    proposed_solution=arguments["proposed_solution"],
                    success_criteria=arguments["success_criteria"],
                    author=arguments["author"],
                    alternatives_considered=arguments.get("alternatives_considered"),
                    risks=arguments.get("risks"),
                )
                return [
                    TextContent(
                        type="text",
                        text=f"Created design doc for ticket {arguments['ticket_id']}. Needs 2 approvals.",
                    )
                ]
            
            elif name == "approve_design":
                result = self.workflow_manager.approve_design(
                    ticket_id=arguments["ticket_id"],
                    approver=arguments["approver"],
                )
                return [TextContent(type="text", text=result)]
            
            elif name == "start_work":
                result = self.workflow_manager.start_work(
                    ticket_id=arguments["ticket_id"],
                    assignee=arguments["assignee"],
                )
                return [TextContent(type="text", text=result)]
            
            elif name == "submit_for_review":
                result = self.workflow_manager.submit_for_review(
                    ticket_id=arguments["ticket_id"],
                    pr_url=arguments["pr_url"],
                )
                return [TextContent(type="text", text=result)]
            
            elif name == "complete_validation":
                result = self.workflow_manager.complete_validation(
                    ticket_id=arguments["ticket_id"],
                    validation_notes=arguments["validation_notes"],
                )
                return [TextContent(type="text", text=result)]
            
            elif name == "get_ready_tickets":
                tickets = self.workflow_manager.get_ready_tickets()
                ticket_list = "\n".join([f"- {t.id}: {t.title}" for t in tickets])
                return [
                    TextContent(
                        type="text",
                        text=f"Ready tickets:\n{ticket_list}" if tickets else "No tickets ready",
                    )
                ]
            
            elif name == "update_wip_limit":
                result = self.workflow_manager.update_wip_limit(arguments["limit"])
                return [TextContent(type="text", text=result)]
            
            else:
                raise ValueError(f"Unknown tool: {name}")

    async def run(self) -> None:
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(read_stream, write_stream, self.server.create_initialization_options())


async def main() -> None:
    """Main entry point for the MCP server."""
    server = GolazoMCPServer()
    await server.run()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
