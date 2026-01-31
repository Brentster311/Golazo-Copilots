# GCP2-001c: Golazo Protocol + CLI

**Status**: BACKLOG  
**Priority**: High  
**Size**: M  
**Created**: 2026-01-27  
**Parent**: GCP2-001

---

## User Story

- **Title**: Golazo Protocol + CLI
- **As a**: Developer or IDE extension
- **I want**: A standard protocol and CLI to interact with the Golazo agent
- **So that**: I can query status, manage work items, and control workflow

- **Out of scope**:
  - State machine logic (GCP2-001a)
  - Consent detection (GCP2-001b)
  - Copilot/MCP integration (GCP2-001d)
  - GUI/IDE extension UI (GCP2-005)

- **Assumptions**:
  - **Assumption (explicit)**: JSON-RPC 2.0 over stdio for protocol
  - **Assumption (explicit)**: CLI uses argparse or click library
  - **Assumption (explicit)**: Server mode started via `golazo serve`

- **Acceptance Criteria**:
  - [ ] CLI commands: `status`, `list`, `switch`, `create`, `transition`, `dor`, `dod`
  - [ ] `golazo serve` starts JSON-RPC server over stdio
  - [ ] Protocol methods: `golazo/status`, `golazo/list`, `golazo/switch`, `golazo/transition`
  - [ ] Protocol notification: `golazo/stateChanged` sent on state changes
  - [ ] Clear error messages for invalid commands
  - [ ] Protocol errors follow JSON-RPC 2.0 specification
  - [ ] `--format json` flag for machine-readable CLI output

- **Non-functional requirements**:
  - CLI response time < 500ms for all commands
  - Protocol must support concurrent requests (though single client)
  - Help text for all commands (`golazo --help`, `golazo status --help`)

- **Telemetry / metrics expected**:
  - None for MVP

- **Rollout / rollback notes**:
  - CLI is the primary interface for testing and standalone use

---

## CLI Usage Examples

```bash
# Check current status
$ golazo status
Work Item: GCP2-001c
Phase: Development
Role: Developer
DoR: ✓ Complete
DoD: 3/7 items complete

# List all work items
$ golazo list
ID          Phase        Role          Profile    Last Active
──────────────────────────────────────────────────────────────
GCP2-001c   development  developer     complete   2 min ago    ← active
GCP2-002    design       architect     complete   1 hour ago

# Create new work item
$ golazo create GCP2-008 --profile express
Created GCP2-008 with Express profile
```

---

## Protocol Specification

### Request (JSON-RPC 2.0)
```json
{"jsonrpc": "2.0", "id": 1, "method": "golazo/status", "params": {}}
```

### Response
```json
{"jsonrpc": "2.0", "id": 1, "result": {"workItemId": "GCP2-001c", "role": "developer", ...}}
```

---

## Dependencies

- GCP2-001a (State machine)
- GCP2-001b (Consent enforcer)
- GCP2-003 (State schema)
# Check current status
$ golazo status
Work Item: GCP2-001c
Phase: Development
Role: Developer
Profile: Complete
DoR: ? Complete
DoD: 3/7 items complete

# List all work items
$ golazo list
ID          Phase        Role          Profile    Last Active
??????????????????????????????????????????????????????????????
GCP2-001c   development  developer     complete   2 min ago    ? active
GCP2-002    design       architect     complete   1 hour ago
GCP2-003    complete     -             complete   yesterday

# Create new work item
$ golazo create GCP2-008 --profile express
Created GCP2-008 with Express profile
Switched to GCP2-008

# Switch work item
$ golazo switch GCP2-002
Switched to GCP2-002 (Design phase, Architect role)

# Show DoR checklist
$ golazo dor
Definition of Ready:
  ? User Story exists
  ? Scope bounded
  ? Test cases documented
  ? Design document approved
```

## Protocol Specification

### Request Format (JSON-RPC 2.0)
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "golazo/status",
  "params": {}
}
```

### Response Format
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "workItemId": "GCP2-001c",
    "phase": "development",
    "role": "developer",
    "profile": "complete",
    "dor": { "complete": true, "items": [...] },
    "dod": { "complete": false, "items": [...] }
  }
}
```

### Notification Format
```json
{
  "jsonrpc": "2.0",
  "method": "golazo/stateChanged",
  "params": {
    "workItemId": "GCP2-001c",
    "previousRole": "tester",
    "currentRole": "developer"
  }
}
```

## Out of Scope

- State machine logic (GCP2-001a)
- Consent detection (GCP2-001b)
- Copilot integration (GCP2-001d)
- IDE extensions (GCP2-005)

## Dependencies

- GCP2-001a (State machine)
- GCP2-001b (Consent enforcer)
- GCP2-003 (State schema)

## Technical Notes

- Use `argparse` or `click` for CLI
- JSON-RPC server using `jsonrpc` library or custom
- Stdio communication for IDE integration
- Consider adding `--format json` flag for scripting
