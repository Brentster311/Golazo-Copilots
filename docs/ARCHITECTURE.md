# Architecture Documentation

## Overview

Golazo-Copilots is a Model Context Protocol (MCP) based system that implements the Microsoft Golazo software development process. The architecture consists of three main layers:

1. **Data Models Layer** - Core domain models
2. **Orchestration Layer** - Workflow management and orchestration
3. **MCP Server Layer** - Protocol implementation for AI integration

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    AI Clients                            │
│            (Claude, ChatGPT, etc.)                       │
└──────────────────┬──────────────────────────────────────┘
                   │ MCP Protocol
                   ▼
┌─────────────────────────────────────────────────────────┐
│                 MCP Server Layer                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │         GolazoMCPServer                          │   │
│  │  • Resources (workflow state, tickets, WIP)      │   │
│  │  • Tools (create, approve, review, validate)     │   │
│  │  • Prompts (workflow templates)                  │   │
│  └──────────────────┬───────────────────────────────┘   │
└─────────────────────┼───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│              Orchestration Layer                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │      WorkflowOrchestrator                        │   │
│  │  • Multi-step workflow execution                 │   │
│  │  • Dependency management                         │   │
│  │  • Policy enforcement                            │   │
│  │  • Audit logging                                 │   │
│  └──────────────────┬───────────────────────────────┘   │
│                     │                                    │
│  ┌──────────────────▼───────────────────────────────┐   │
│  │      WorkflowManager                             │   │
│  │  • Ticket lifecycle management                   │   │
│  │  • Design doc approvals                          │   │
│  │  • WIP limit enforcement                         │   │
│  │  • Status transitions                            │   │
│  └──────────────────┬───────────────────────────────┘   │
└─────────────────────┼───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│               Data Models Layer                          │
│  • Ticket (work items)                                   │
│  • DesignDoc (design documents)                          │
│  • WorkflowState (board state)                           │
│  • CodeReview (review metadata)                          │
│  • Workflow (orchestrator workflows)                     │
└─────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Data Models (`golazo_copilots/models/`)

#### Ticket
Represents a work item in the Golazo process.

**States:**
- BACKLOG → DESIGN → DESIGN_REVIEW → READY → IN_PROGRESS → CODE_REVIEW → VALIDATION → DONE

**Priority Levels:**
- SWARM: Urgent, drop everything
- INTERRUPT: Important but not urgent
- PLANNED: Normal planned work

#### DesignDoc
Lightweight design document attached to tickets.

**Requirements:**
- Must have 2 peer approvals before ticket becomes READY
- Contains problem statement, proposed solution, success criteria
- Optional: alternatives considered, risks

#### WorkflowState
Current state of the workflow board.

**Tracks:**
- All tickets
- Current WIP count
- WIP limit
- Team members

### 2. Orchestration Layer (`golazo_copilots/orchestrator/`)

#### WorkflowManager
Core business logic for the Golazo process.

**Responsibilities:**
- Create and manage tickets
- Enforce WIP limits
- Track design approvals
- Manage ticket state transitions
- Provide workflow state queries

**Key Methods:**
```python
create_ticket(title, description, priority, created_by)
create_design_doc(ticket_id, title, problem_statement, ...)
approve_design(ticket_id, approver)
start_work(ticket_id, assignee)  # Checks WIP limits
submit_for_review(ticket_id, pr_url)
complete_validation(ticket_id, validation_notes)
```

#### WorkflowOrchestrator
Manages complex multi-step workflows.

**Features:**
- Dependency-based execution order
- Parallel step execution (configurable)
- Policy enforcement
- Comprehensive audit logging

**Workflow Policies:**
- require_design_approval
- enforce_wip_limits
- require_code_review
- require_validation
- min_design_approvals
- max_parallel_steps

### 3. MCP Server Layer (`golazo_copilots/servers/`)

#### GolazoMCPServer
MCP protocol implementation exposing Golazo capabilities to AI clients.

**Resources:**
```
golazo://workflow/state    - Current workflow state
golazo://workflow/tickets  - All tickets
golazo://workflow/wip      - WIP status
```

**Tools:**
- create_ticket
- create_design_doc
- approve_design
- start_work
- submit_for_review
- complete_validation
- get_ready_tickets
- update_wip_limit

## Workflow Patterns

### Pattern 1: Basic Feature Development

```
1. Create ticket (BACKLOG)
2. Create design doc (DESIGN → DESIGN_REVIEW)
3. Get 2 approvals (DESIGN_REVIEW → READY)
4. Start work (READY → IN_PROGRESS)
5. Submit for review (IN_PROGRESS → CODE_REVIEW)
6. Complete validation (CODE_REVIEW → DONE)
```

### Pattern 2: Orchestrated Workflow

```python
workflow = orchestrator.create_workflow(
    name="Feature Development",
    steps=[
        {"action": "create_design_doc", ...},
        {"action": "approve_design", "dependencies": ["create_design_doc"], ...},
        {"action": "start_work", "dependencies": ["approve_design"], ...},
        # ... more steps
    ]
)

result = await orchestrator.execute_workflow(workflow.id, actor="alice")
```

## Policy Enforcement

### WIP Limits
- Default limit: 3 concurrent in-progress tickets
- Enforced when calling `start_work()`
- Configurable via `update_wip_limit()`

### Design Approvals
- Minimum 2 peer approvals required
- Approver cannot approve their own design
- Automatic transition to READY when threshold met

### Audit Trail
All workflow actions are logged:
- Timestamp
- Actor
- Action
- Status
- Details

## Extension Points

### Custom Action Handlers
Add new actions to the orchestrator:

```python
orchestrator.action_handlers["custom_action"] = custom_handler
```

### Custom Policies
Extend WorkflowPolicy:

```python
class CustomPolicy(WorkflowPolicy):
    require_security_review: bool = True
    min_test_coverage: float = 0.8
```

### Custom Resources
Add new MCP resources:

```python
@server.list_resources()
async def list_resources():
    return [
        Resource(uri="golazo://custom/resource", ...),
        # ...
    ]
```

## Data Flow

### Ticket Creation Flow
```
Client → MCP Tool Call → GolazoMCPServer
  → WorkflowManager.create_ticket()
  → New Ticket in BACKLOG state
  → Response to Client
```

### Design Approval Flow
```
Client → MCP Tool Call → GolazoMCPServer
  → WorkflowManager.approve_design()
  → Check: ticket has design doc
  → Add approval to design doc
  → Check: >= 2 approvals?
    → Yes: Transition ticket to READY
    → No: Keep in DESIGN_REVIEW
  → Response to Client
```

### WIP Enforcement Flow
```
Client → start_work() → WorkflowManager
  → Get current WIP count
  → Check: current_wip < wip_limit?
    → Yes: Transition to IN_PROGRESS
    → No: Raise ValueError
  → Response
```

## Scalability Considerations

### State Management
Currently in-memory. For production:
- Add persistence layer (database)
- Implement state snapshots
- Add event sourcing for audit trail

### Concurrency
For multi-user scenarios:
- Add locking mechanism
- Implement optimistic concurrency control
- Use message queue for workflow steps

### Performance
- Cache workflow state queries
- Index tickets by status
- Batch audit log writes

## Security Considerations

### Authentication
- MCP server runs in trusted environment
- Client authentication via MCP protocol
- Actor identification in all actions

### Authorization
- Role-based access control (future)
- Policy-based permissions (future)
- Audit logging for compliance

### Data Validation
- Pydantic models for type safety
- Input validation on all operations
- State transition validation

## Testing Strategy

### Unit Tests
- Model validation
- Workflow manager operations
- State transitions
- Policy enforcement

### Integration Tests
- MCP server protocol compliance
- End-to-end workflows
- Orchestrator execution
- Error handling

### Example Tests
```python
def test_wip_limit_enforcement():
    wm = WorkflowManager()
    # Create > WIP limit tickets
    # Assert: can only start up to limit
    
def test_design_approval_transition():
    wm = WorkflowManager()
    # Create ticket with design
    # Add 2 approvals
    # Assert: ticket state is READY
```

## Future Enhancements

1. **Persistence Layer**
   - PostgreSQL/SQLite backend
   - Event sourcing
   - State snapshots

2. **Advanced Orchestration**
   - Conditional branching
   - Retry policies
   - Parallel workflows

3. **Metrics & Analytics**
   - Cycle time tracking
   - Throughput metrics
   - Bottleneck detection

4. **Integration**
   - GitHub integration
   - Slack notifications
   - Jira sync

5. **UI Dashboard**
   - Visual workflow board
   - Real-time updates
   - Metrics visualization
