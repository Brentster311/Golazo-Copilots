"""Command-line interface for Golazo Copilots."""

import asyncio
import json
from typing import Optional
import argparse

from golazo_copilots.orchestrator import WorkflowManager, WorkflowOrchestrator
from golazo_copilots.models import TicketPriority


def create_ticket_command(args):
    """Create a new ticket."""
    wm = WorkflowManager()
    ticket = wm.create_ticket(
        title=args.title,
        description=args.description,
        priority=TicketPriority(args.priority),
        created_by=args.created_by,
        estimated_days=args.estimated_days,
    )
    print(f"Created ticket: {ticket.id}")
    print(f"Title: {ticket.title}")
    print(f"Status: {ticket.status}")
    return ticket


def list_tickets_command(args):
    """List all tickets."""
    wm = WorkflowManager()
    tickets = wm.list_tickets()
    
    if not tickets:
        print("No tickets found.")
        return
    
    print(f"Total tickets: {len(tickets)}")
    print()
    for ticket in tickets:
        print(f"ID: {ticket.id}")
        print(f"  Title: {ticket.title}")
        print(f"  Status: {ticket.status}")
        print(f"  Priority: {ticket.priority}")
        print(f"  Created by: {ticket.created_by}")
        print()


def wip_status_command(args):
    """Show WIP status."""
    wm = WorkflowManager()
    status = wm.get_wip_status()
    
    print("Work In Progress Status:")
    print(f"  Current WIP: {status['current_wip']}")
    print(f"  WIP Limit: {status['wip_limit']}")
    print(f"  Available Slots: {status['available_slots']}")


async def run_server_command(args):
    """Run the MCP server."""
    from golazo_copilots.servers import GolazoMCPServer
    
    print("Starting Golazo MCP Server...")
    print("Connect your AI client to this server to use Golazo workflows.")
    
    server = GolazoMCPServer()
    await server.run()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Golazo Copilots - MCP-based Golazo workflow automation"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Create ticket command
    create_parser = subparsers.add_parser("create-ticket", help="Create a new ticket")
    create_parser.add_argument("title", help="Ticket title")
    create_parser.add_argument("description", help="Ticket description")
    create_parser.add_argument(
        "--priority",
        choices=["swarm", "interrupt", "planned"],
        default="planned",
        help="Ticket priority",
    )
    create_parser.add_argument("--created-by", required=True, help="Creator username")
    create_parser.add_argument(
        "--estimated-days", type=float, help="Estimated days to complete"
    )
    create_parser.set_defaults(func=create_ticket_command)
    
    # List tickets command
    list_parser = subparsers.add_parser("list-tickets", help="List all tickets")
    list_parser.set_defaults(func=list_tickets_command)
    
    # WIP status command
    wip_parser = subparsers.add_parser("wip-status", help="Show WIP status")
    wip_parser.set_defaults(func=wip_status_command)
    
    # Server command
    server_parser = subparsers.add_parser("server", help="Run the MCP server")
    server_parser.set_defaults(func=run_server_command)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if asyncio.iscoroutinefunction(args.func):
        asyncio.run(args.func(args))
    else:
        args.func(args)


if __name__ == "__main__":
    main()
