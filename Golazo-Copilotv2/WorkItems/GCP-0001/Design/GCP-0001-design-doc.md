# GCP-0001 Design Document: Initialize Work Item

## Summary

Implement the `gcp_init` MCP tool that creates a new Golazo Copilot work item with persistent state tracking. This is the foundational vertical slice enabling all subsequent workflow functionality.

---

## Problem Statement

GitHub Copilot users following the Golazo workflow currently have no persistent state tracking. Workflow progress is lost between sessions, there's no programmatic way to enforce gates, and role transitions rely on LLM memory which is unreliable.

**GCP-0001** solves the "cold start" problem: How does a user begin a tracked workflow session?

---

## Business Case

### Why Now
- Golazo V1 (markdown-only) has proven the workflow concept but lacks enforcement
- MCP (Model Context Protocol) is now available in GitHub Copilot, enabling programmatic tools
- Teams are losing productivity re-explaining context between sessions

### Impact
- **Time saved**: Eliminates re-establishing workflow context (~5-10 min/session)
- **Consistency**: Every work item starts with identical structure
- **Foundation**: Enables all subsequent GCP work items

### KPIs
- Work items can be created via MCP tool
- State persists across IDE restarts
- Role instructions are served correctly

---

## Stakeholders

| Role | Interest |
|------|----------|
| Developer (primary user) | Needs simple "Start X" command to begin tracked work |
| Team Lead | Wants consistent artifact structure across team |
| Future Golazo Copilot maintainers | Need clean, extensible codebase |

---

## Functional Requirements

### FR1: Create Work Item State
- `gcp_init({ workItemId, profile })` creates `WorkItems/{id}/state.json`
- State schema includes: workItemId, profile, currentRole, currentPhase, dor, dod, roleHistory, deviations, timestamps

### FR2: Serve Role Instructions
- Return project-owner role instructions on init
- Check local `.github/roles/project-owner.md` first
- Fall back to package default if local doesn't exist

### FR3: MCP Resource Exposure
- `state://current` resource returns active work item state
- Error if no work item active

### FR4: Input Validation
- workItemId: alphanumeric, hyphens, underscores only
- profile: must be "complete", "express", or "spike"
- Reject duplicate work item IDs

---

## Non-Functional Requirements

### NFR1: Performance
- Init completes in <100ms (just file I/O)
- No network calls required

### NFR2: Reliability
- Atomic file writes to prevent corruption
- Schema version for future migrations

### NFR3: Portability
- Works on Windows, macOS, Linux
- No native dependencies

### NFR4: Testability
- All core logic unit testable
- File system interactions mockable

---

## Proposed Approach

### Technology Stack
- **Runtime**: Python 3.10+
- **MCP SDK**: mcp (Python MCP SDK)
- **Models**: Pydantic for type validation
- **Test**: pytest

### Package Structure
```
golazo_copilot/
??? pyproject.toml
??? src/
?   ??? golazo_copilot/
?       ??? __init__.py
?       ??? server.py             # MCP server entry
?       ??? tools/
?       ?   ??? __init__.py
?       ?   ??? gcp_init.py       # gcp_init tool handler
?       ??? resources/
?       ?   ??? __init__.py
?       ?   ??? state_current.py  # state://current resource
?       ??? core/
?       ?   ??? __init__.py
?       ?   ??? types.py          # Pydantic models
?       ?   ??? state.py          # State creation/validation
?       ?   ??? persistence.py    # File I/O with atomic writes
?       ??? roles/
?           ??? __init__.py
?           ??? loader.py         # Role instruction loading
?           ??? defaults/
?               ??? *.md          # Default role files
??? tests/
    ??? __init__.py
    ??? test_gcp_init.py
    ??? test_state.py
    ??? test_persistence.py
```

### Implementation Sequence
1. **Persistence layer**: JSON read/write with atomic saves
2. **State creation**: Pydantic models, validation, defaults
3. **Role loader**: Local override + package default
4. **MCP tool**: gcp_init wiring
5. **MCP resource**: state://current
6. **Default role files**: All 8 role markdown files

---

## Alternatives Considered

| Alternative | Pros | Cons | Decision |
|-------------|------|------|----------|
| SQLite instead of JSON | Query capabilities | Adds complexity, overkill for single-doc | **Rejected** |
| YAML instead of JSON | More readable | Needs extra parser | **Rejected** |
| Store state in memory only | Simpler | Loses on restart, defeats purpose | **Rejected** |
| dataclasses instead of Pydantic | No dependency | Less validation, no JSON schema | **Rejected** |

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| File permission issues | Medium | High | Clear error messages, document required permissions |
| Schema changes break old state | Medium | Medium | Schema version field, migration support in future |
| Role file not found | Low | Medium | Graceful fallback to package defaults |
| MCP SDK breaking changes | Low | High | Pin SDK version, integration tests |

---

## Open Questions

1. **Q**: Should we create the WorkItems directory if it doesn't exist?
   **A**: Yes, with a confirmation message

2. **Q**: What if user runs gcp_init twice with same ID?
   **A**: Error with suggestion to use gcp_switch

3. **Q**: Should profile default be configurable per-repo?
   **A**: Future scope (GCP-0008 or later)

---

## Dependencies

### External
- Node.js 18+ (LTS)
- @modelcontextprotocol/sdk (npm)

### Internal
- None (this is the foundation)

---

## Migration / Rollout Plan

### Phase 1: Package Development
- Implement in `golazo-copilot` npm package
- Publish to npm as `golazo-copilot`

### Phase 2: User Installation
```bash
npm install -g golazo-copilot
```

### Phase 3: IDE Configuration
- VS Code: Add to MCP server settings
- Other IDEs: Per-IDE documentation

### Rollback
- User can `npm uninstall -g golazo-copilot`
- State files remain (can be deleted manually)

---

## Observability Plan

### Logging
- Info: Work item created, role loaded
- Warn: Local role file not found, using default
- Error: File write failed, invalid input

### No Telemetry
- Privacy-first: No data leaves local machine
- Errors visible in MCP server logs / IDE output

---

## Test Strategy Summary

### Unit Tests
- State creation with various inputs
- Validation (valid/invalid workItemIds)
- Role loader (local override, fallback)
- Atomic file write

### Integration Tests
- Full gcp_init flow with mocked file system
- MCP tool registration and invocation

### Manual Tests
- End-to-end in VS Code with Copilot
- Verify state.json created correctly
- Verify role instructions returned

---

## Appendix: State Schema v1.0

```typescript
interface WorkItemState {
  schemaVersion: "1.0";
  workItemId: string;
  profile: "complete" | "express" | "spike";
  currentPhase: "definition" | "development" | "completion";
  currentRole: string;
  createdAt: string;
  updatedAt: string;
  dor: Record<string, boolean>;
  dod: Record<string, boolean>;
  roleHistory: Array<{
    role: string;
    enteredAt: string;
    exitedAt: string | null;
  }>;
  deviations: Array<{
    action: string;
    reason: string;
    role: string;
    timestamp: string;
  }>;
}
```
