# Examples

This directory contains examples demonstrating how to use Golazo-Copilots.

## Workflow Examples

Run the workflow examples to see the system in action:

```bash
python examples/workflow_examples.py
```

This will demonstrate:
1. **Basic Workflow**: Creating tickets, design docs, approvals, and progression
2. **WIP Limit Enforcement**: How the system enforces work-in-progress limits
3. **Complete Feature Workflow**: End-to-end orchestrated workflow

## MCP Configuration

To use the Golazo MCP server with an AI client (like Claude Desktop):

1. Copy `mcp_config.json` to your MCP configuration directory
2. Adjust paths as needed for your environment
3. Restart your AI client

Example configuration file: `mcp_config.json`

## Using the CLI

The CLI provides basic commands for interacting with Golazo workflows:

```bash
# Create a ticket
python -m golazo_copilots.cli create-ticket \
  "Add authentication" \
  "Implement JWT authentication" \
  --priority planned \
  --created-by alice \
  --estimated-days 3

# List all tickets
python -m golazo_copilots.cli list-tickets

# Show WIP status
python -m golazo_copilots.cli wip-status

# Run the MCP server
python -m golazo_copilots.cli server
```

## Programmatic Usage

See `workflow_examples.py` for detailed examples of using the API programmatically.

### Quick Start

```python
from golazo_copilots.orchestrator import WorkflowManager
from golazo_copilots.models import TicketPriority

# Initialize
wm = WorkflowManager()

# Create a ticket
ticket = wm.create_ticket(
    title="My Feature",
    description="Feature description",
    priority=TicketPriority.PLANNED,
    created_by="alice"
)

# Create design doc
design = wm.create_design_doc(
    ticket_id=ticket.id,
    title="Design",
    problem_statement="Problem to solve",
    proposed_solution="How to solve it",
    success_criteria="How we know it's done",
    author="alice"
)

# Get approvals
wm.approve_design(ticket.id, "bob")
wm.approve_design(ticket.id, "charlie")

# Start work
wm.start_work(ticket.id, "alice")
```

## MCP Server Usage

Once the server is running, you can use it from any MCP-compatible AI client:

```
User: Create a new ticket for implementing user authentication
AI: [Uses create_ticket tool]

User: What tickets are ready to work on?
AI: [Uses get_ready_tickets tool]

User: Show me the current WIP status
AI: [Reads golazo://workflow/wip resource]
```
