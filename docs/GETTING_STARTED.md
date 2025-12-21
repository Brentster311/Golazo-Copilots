# Getting Started with Golazo-Copilots

This guide will help you get started with Golazo-Copilots, an MCP-based system for implementing the Golazo software development process.

## What is Golazo-Copilots?

Golazo-Copilots combines:
- **Microsoft Golazo Process**: A lean development methodology
- **Model Context Protocol (MCP)**: AI tool integration standard
- **Workflow Orchestration**: Multi-step automation with policy enforcement

## Installation

### Prerequisites

- Python 3.10 or higher
- pip package manager

### Install from Source

```bash
# Clone the repository
git clone https://github.com/Brentster311/Golazo-Copilots.git
cd Golazo-Copilots

# Install the package
pip install -e .

# For development (with testing tools)
pip install -e ".[dev]"
```

## Quick Start

### 1. Basic Workflow Management

```python
from golazo_copilots.orchestrator import WorkflowManager
from golazo_copilots.models import TicketPriority

# Initialize the workflow manager
wm = WorkflowManager()

# Create a ticket
ticket = wm.create_ticket(
    title="Implement user authentication",
    description="Add JWT-based authentication to the API",
    priority=TicketPriority.PLANNED,
    created_by="alice",
    estimated_days=3.0
)

print(f"Created ticket: {ticket.id}")
```

### 2. Design-First Development

```python
# Create a design document
design_doc = wm.create_design_doc(
    ticket_id=ticket.id,
    title="Authentication Design",
    problem_statement="Users need secure authentication",
    proposed_solution="Implement JWT tokens with refresh rotation",
    success_criteria="Users can login and maintain session securely",
    author="alice",
    risks="Need to handle token expiration gracefully"
)

# Get peer approvals (need 2)
wm.approve_design(ticket.id, "bob")
wm.approve_design(ticket.id, "charlie")

# Ticket is now READY for implementation
```

### 3. Working with WIP Limits

```python
# Check current WIP status
wip_status = wm.get_wip_status()
print(f"Current WIP: {wip_status['current_wip']}/{wip_status['wip_limit']}")

# Start work (enforces WIP limits)
wm.start_work(ticket.id, "alice")

# Submit for review
wm.submit_for_review(ticket.id, "https://github.com/org/repo/pull/123")

# Complete customer validation
wm.complete_validation(
    ticket.id,
    "Tested with 5 users, all features working correctly"
)
```

### 4. Orchestrated Workflows

```python
from golazo_copilots.orchestrator import WorkflowOrchestrator

# Create orchestrator
orchestrator = WorkflowOrchestrator(wm)

# Define a multi-step workflow
workflow = orchestrator.create_workflow(
    name="Feature Development",
    description="Complete feature workflow",
    steps=[
        {
            "name": "create_design",
            "action": "create_design_doc",
            "parameters": {...}
        },
        {
            "name": "approve_design",
            "action": "approve_design",
            "parameters": {...},
            "dependencies": ["create_design"]  # Runs after design creation
        },
        # ... more steps
    ]
)

# Execute the workflow
result = await orchestrator.execute_workflow(workflow.id, actor="alice")
print(f"Workflow status: {result['status']}")
```

## Using the CLI

The CLI provides quick access to common operations:

```bash
# Create a ticket
golazo create-ticket \
  "Add search feature" \
  "Implement full-text search" \
  --priority planned \
  --created-by alice \
  --estimated-days 5

# Check WIP status
golazo wip-status

# List all tickets
golazo list-tickets
```

## Running the MCP Server

### Start the Server

```bash
# Using the CLI
golazo-server

# Or using Python
python -m golazo_copilots.servers.golazo_server
```

### Configure AI Client

Add to your MCP client configuration (e.g., Claude Desktop):

```json
{
  "mcpServers": {
    "golazo": {
      "command": "python",
      "args": ["-m", "golazo_copilots.servers.golazo_server"]
    }
  }
}
```

### Using from AI Client

Once configured, you can interact naturally:

```
You: Create a ticket for implementing user profiles
AI: [Uses create_ticket tool]

You: What tickets are ready to work on?
AI: [Uses get_ready_tickets tool]

You: Show the workflow state
AI: [Reads golazo://workflow/state resource]
```

## Understanding the Workflow

### Ticket States

```
BACKLOG → DESIGN → DESIGN_REVIEW → READY → IN_PROGRESS → CODE_REVIEW → VALIDATION → DONE
```

1. **BACKLOG**: Initial ticket creation
2. **DESIGN**: Design document created
3. **DESIGN_REVIEW**: Awaiting peer approvals (need 2)
4. **READY**: Design approved, ready to start
5. **IN_PROGRESS**: Work in progress (respects WIP limits)
6. **CODE_REVIEW**: Code submitted for review
7. **VALIDATION**: Customer validation in progress
8. **DONE**: Validated and complete

### Priority Levels

- **SWARM**: Urgent, drop everything (production issues)
- **INTERRUPT**: Important but not urgent (bugs)
- **PLANNED**: Normal planned work (features)

### WIP Limits

- Default: 3 concurrent in-progress tickets
- Prevents team overload
- Encourages finishing work before starting new work
- Configurable per team

## Key Concepts

### Design Documents

Every ticket requires a lightweight design document with:
- **Problem Statement**: What problem are we solving?
- **Proposed Solution**: How will we solve it?
- **Success Criteria**: How do we know it's done?
- **Alternatives Considered**: What else did we consider?
- **Risks**: What could go wrong?

### Peer Reviews

- Minimum 2 peer approvals required for design docs
- Spreads knowledge across the team
- Catches issues early, before coding
- Reduces surprises during code review

### Customer Validation

- "Done" means customer has validated the value
- Not just code merged or tests passing
- Explicit validation stage in the workflow
- Ensures delivered value, not just completed work

## Next Steps

1. **Run the examples**: `python examples/workflow_examples.py`
2. **Read the architecture**: See `docs/ARCHITECTURE.md`
3. **Try the CLI**: Experiment with `golazo` commands
4. **Set up MCP**: Configure your AI client
5. **Build workflows**: Create custom orchestrated workflows

## Common Patterns

### Pattern 1: Bug Fix

```python
# High priority, small scope
ticket = wm.create_ticket(
    title="Fix login timeout",
    description="Users logged out too quickly",
    priority=TicketPriority.INTERRUPT,
    created_by="bob",
    estimated_days=0.5
)
# ... create design, get approvals, fix, validate
```

### Pattern 2: Feature Development

```python
# Normal priority, larger scope
ticket = wm.create_ticket(
    title="User profile page",
    description="Complete user profile functionality",
    priority=TicketPriority.PLANNED,
    created_by="alice",
    estimated_days=5.0
)
# ... create detailed design, get approvals, implement, validate
```

### Pattern 3: Production Incident

```python
# Highest priority, immediate action
ticket = wm.create_ticket(
    title="Database down",
    description="Production database not responding",
    priority=TicketPriority.SWARM,
    created_by="oncall",
    estimated_days=0.25
)
# ... minimal design, quick approvals, fix, validate
```

## Troubleshooting

### WIP Limit Exceeded

```python
# Error: WIP limit reached (3). Complete existing work...

# Solution 1: Complete existing work
wm.complete_validation(existing_ticket_id, "Validated")

# Solution 2: Increase WIP limit (not recommended)
wm.update_wip_limit(5)
```

### Design Not Approved

```python
# Error: Ticket must be in READY status

# Solution: Get required approvals
wm.approve_design(ticket.id, "reviewer1")
wm.approve_design(ticket.id, "reviewer2")
```

### Ticket Not Found

```python
# Error: Ticket TICKET-xxx not found

# Solution: Check ticket ID
tickets = wm.list_tickets()
for ticket in tickets:
    print(f"{ticket.id}: {ticket.title}")
```

## Getting Help

- **Documentation**: See `docs/` directory
- **Examples**: See `examples/` directory
- **Issues**: Open an issue on GitHub
- **Contributing**: See `CONTRIBUTING.md`

## Resources

- [Microsoft Golazo Documentation](https://microsoft.github.io/golazo/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Project Repository](https://github.com/Brentster311/Golazo-Copilots)
