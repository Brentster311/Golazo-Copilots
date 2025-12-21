# Golazo-Copilots

A Model Context Protocol (MCP) based orchestrator implementing the [Microsoft Golazo](https://microsoft.github.io/golazo/) software development process. This system enables AI-powered automation of lean software development workflows with built-in policy enforcement, audit logging, and workflow orchestration.

## Overview

Golazo-Copilots combines:
- **Microsoft Golazo Process**: A lean, Kanban-inspired development methodology emphasizing lightweight design docs, WIP limits, peer reviews, and customer validation
- **Model Context Protocol (MCP)**: Standardized protocol for connecting AI tools to workflows and data sources
- **Workflow Orchestrator**: Multi-step task automation with policy enforcement and audit trails

## Key Features

### Golazo Process Implementation
- ✅ **Design-First Workflow**: Mandatory design documents with peer approvals before implementation
- ✅ **WIP Limits**: Enforced work-in-progress limits to maintain focus and flow
- ✅ **Shared Ownership**: Any team member can pick up any ready ticket
- ✅ **Customer Validation**: Explicit validation stage ensuring delivered value
- ✅ **Priority Rails**: Support for Swarm (urgent), Interrupt, and Planned work

### MCP Server Capabilities
- **Resources**: Access workflow state, tickets, and WIP status
- **Tools**: Create tickets, design docs, approvals, reviews, and validations
- **Real-time State**: Live workflow board state accessible to AI agents

### Orchestrator Features
- **Multi-step Workflows**: Chain complex sequences of actions
- **Dependency Management**: Steps execute only when dependencies are met
- **Policy Enforcement**: Configurable rules for design approvals, reviews, and validation
- **Audit Logging**: Complete audit trail of all workflow actions
- **Parallel Execution**: Configurable parallel step execution

## Installation

```bash
# Clone the repository
git clone https://github.com/Brentster311/Golazo-Copilots.git
cd Golazo-Copilots

# Install dependencies
pip install -e .

# For development
pip install -e ".[dev]"
```

## Quick Start

### Running the MCP Server

```bash
python -m golazo_copilots.servers.golazo_server
```

### Using the Workflow Manager

```python
from golazo_copilots.orchestrator import WorkflowManager
from golazo_copilots.models import TicketPriority

# Initialize the workflow manager
wm = WorkflowManager()

# Create a ticket
ticket = wm.create_ticket(
    title="Add user authentication",
    description="Implement JWT-based authentication",
    priority=TicketPriority.PLANNED,
    created_by="alice",
    estimated_days=3.0
)

# Create a design document
design_doc = wm.create_design_doc(
    ticket_id=ticket.id,
    title="Authentication Design",
    problem_statement="Need secure user authentication",
    proposed_solution="Use JWT tokens with refresh token rotation",
    success_criteria="Users can login and maintain session",
    author="alice"
)

# Approve the design (needs 2 approvals)
wm.approve_design(ticket.id, "bob")
wm.approve_design(ticket.id, "charlie")  # Now ticket is READY

# Start work
wm.start_work(ticket.id, "alice")

# Submit for review
wm.submit_for_review(ticket.id, "https://github.com/org/repo/pull/123")

# Complete validation
wm.complete_validation(ticket.id, "Tested in staging, login works perfectly")
```

### Using the Orchestrator

```python
from golazo_copilots.orchestrator import WorkflowOrchestrator, WorkflowManager

# Setup
wm = WorkflowManager()
orchestrator = WorkflowOrchestrator(wm)

# Define a complete workflow
workflow = orchestrator.create_workflow(
    name="New Feature Development",
    description="Complete workflow from idea to validation",
    steps=[
        {
            "name": "create_ticket",
            "description": "Create initial ticket",
            "action": "create_ticket",
            "parameters": {
                "title": "New feature",
                "description": "Feature description",
                "priority": "planned",
                "created_by": "alice"
            }
        },
        {
            "name": "create_design",
            "description": "Create design doc",
            "action": "create_design_doc",
            "parameters": {
                "ticket_id": "TICKET-xxx",  # Will be filled in
                "title": "Feature Design",
                "problem_statement": "Problem to solve",
                "proposed_solution": "Solution approach",
                "success_criteria": "Definition of done",
                "author": "alice"
            },
            "dependencies": ["create_ticket"]
        },
        # ... more steps
    ]
)

# Execute the workflow
result = await orchestrator.execute_workflow(workflow.id, actor="alice")
print(f"Workflow completed: {result}")
```

## Architecture

```
golazo_copilots/
├── models/              # Pydantic models for tickets, design docs, workflow state
├── servers/             # MCP server implementation
├── orchestrator/        # Workflow manager and orchestrator
│   ├── workflow_manager.py   # Core Golazo workflow management
│   └── orchestrator.py       # Multi-step workflow orchestration
└── tools/               # Future: Additional MCP tools
```

## MCP Tools Reference

### Available Tools

1. **create_ticket**: Create a new work ticket
2. **create_design_doc**: Create a design document for a ticket
3. **approve_design**: Approve a design (requires 2 approvals)
4. **start_work**: Start working on a ticket (checks WIP limits)
5. **submit_for_review**: Submit work for code review
6. **complete_validation**: Complete customer validation and mark done
7. **get_ready_tickets**: List all tickets ready to be picked up
8. **update_wip_limit**: Update the WIP limit

### Available Resources

1. **golazo://workflow/state**: Current workflow state
2. **golazo://workflow/tickets**: All tickets in the system
3. **golazo://workflow/wip**: Current WIP status and limits

## Golazo Process Flow

```
BACKLOG → DESIGN → DESIGN_REVIEW → READY → IN_PROGRESS → CODE_REVIEW → VALIDATION → DONE
```

1. **BACKLOG**: Initial ticket creation
2. **DESIGN**: Design document created
3. **DESIGN_REVIEW**: Awaiting 2 peer approvals
4. **READY**: Design approved, ready for implementation
5. **IN_PROGRESS**: Work has started (respects WIP limits)
6. **CODE_REVIEW**: Code submitted for peer review
7. **VALIDATION**: Customer validation in progress
8. **DONE**: Value validated by customer

## Configuration

### Workflow Policies

```python
from golazo_copilots.orchestrator import WorkflowPolicy

policy = WorkflowPolicy(
    require_design_approval=True,
    enforce_wip_limits=True,
    require_code_review=True,
    require_validation=True,
    min_design_approvals=2,
    max_parallel_steps=3
)
```

## Development

### Running Tests

```bash
pytest
```

### Code Quality

```bash
# Format code
black golazo_copilots/

# Lint
ruff check golazo_copilots/

# Type checking
mypy golazo_copilots/
```

## Principles

Following Golazo's lean principles:
- **Deliver quickly**: Small, value-focused tickets
- **Eliminate waste**: Minimize ceremony, maximize flow
- **Build quality in**: Design docs and peer reviews upfront
- **Create knowledge**: Shared design docs and ownership
- **Respect people**: WIP limits prevent overload
- **Optimize the whole**: Team flow over individual heroics

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Follow existing code style
4. Add tests for new functionality
5. Submit a pull request

## License

See [LICENSE](LICENSE) file for details.

## Resources

- [Microsoft Golazo Documentation](https://microsoft.github.io/golazo/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [MCP Architecture](https://modelcontextprotocol.io/docs/learn/architecture)