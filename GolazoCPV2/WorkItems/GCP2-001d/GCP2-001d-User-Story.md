# GCP2-001d: Copilot/MCP Integration

**Status**: BACKLOG  
**Priority**: High  
**Size**: M  
**Created**: 2026-01-27  
**Parent**: GCP2-001

---

## User Story

- **Title**: Copilot/MCP Integration
- **As a**: Developer using GitHub Copilot
- **I want**: Golazo V2 to integrate with Copilot via MCP tools
- **So that**: Copilot can query and update workflow state during conversations

- **Out of scope**:
  - State machine logic (GCP2-001a)
  - Consent detection logic (GCP2-001b)  
  - CLI commands (GCP2-001c)
  - IDE extension UI (GCP2-005)

- **Assumptions**:
  - **Assumption (explicit)**: MCP (Model Context Protocol) is the integration method
  - **Assumption (explicit)**: Tools communicate with agent via GCP2-001c protocol
  - **Assumption (explicit)**: Tool descriptions guide Copilot behavior

- **Acceptance Criteria**:
  - [ ] MCP tools defined: `golazo_status`, `golazo_transition`, `golazo_skip`
  - [ ] MCP tools defined: `golazo_create`, `golazo_switch`, `golazo_check_dor`, `golazo_check_dod`
  - [ ] Tools return structured responses Copilot can interpret
  - [ ] Unauthorized skip attempts return "denied" status guiding Copilot to ask user
  - [ ] Tool descriptions explicitly state when each tool should be called
  - [ ] MCP server configuration file (`mcp.json`) generated
  - [ ] Tools registered with Copilot via MCP

- **Non-functional requirements**:
  - Tool responses must be concise (Copilot context window limits)
  - Tool descriptions must be unambiguous to guide Copilot behavior
  - Error responses must suggest corrective action

- **Telemetry / metrics expected**:
  - None for MVP

- **Rollout / rollback notes**:
  - Final integration layer; test thoroughly with Copilot before release

---

## MCP Tool Definitions

### golazo_status
```json
{
  "name": "golazo_status",
  "description": "Get current Golazo workflow status. Call at conversation start and after transitions.",
  "parameters": {}
}
```

### golazo_skip
```json
{
  "name": "golazo_skip",
  "description": "Skip roles. ONLY call when user EXPLICITLY requests skip. Include user's exact words.",
  "parameters": {
    "roles": {"type": "array", "items": {"type": "string"}},
    "reason": {"type": "string", "description": "User's exact words"}
  }
}
```

---

## Tool Response Examples

### Blocked Transition
```json
{
  "status": "blocked",
  "reason": "Cannot transition to Developer. DoR incomplete.",
  "suggestion": "Complete Architect role first."
}
```

---

## Dependencies

- GCP2-001a (State machine)
- GCP2-001b (Consent enforcer)
- GCP2-001c (Protocol)
    "reason": {
      "type": "string", 
      "description": "User's exact words requesting the skip"
    }
  }
}
```

## Tool Response Examples

### Successful Status
```json
{
  "status": "ok",
  "workItem": "GCP2-001d",
  "phase": "development",
  "role": "developer",
  "profile": "complete",
  "message": "Currently in Developer role. DoR complete, proceed with implementation."
}
```

### Blocked Transition
```json
{
  "status": "blocked",
  "reason": "Cannot transition to Developer. DoR incomplete.",
  "missing": ["Design document not approved"],
  "suggestion": "Complete Architect role first to approve design."
}
```

### Unauthorized Skip
```json
{
  "status": "denied",
  "reason": "Skip not authorized. No explicit user consent detected.",
  "suggestion": "Ask user if they want to skip roles or use Express profile."
}
```

## Out of Scope

- State machine logic (GCP2-001a)
- Consent detection logic (GCP2-001b)
- CLI (GCP2-001c)
- IDE extensions (GCP2-005)

## Dependencies

- GCP2-001a (State machine)
- GCP2-001b (Consent enforcer)
- GCP2-001c (Protocol for communication)

## Technical Notes

- MCP tools defined in `mcp.json` or equivalent config
- Tools communicate with Golazo agent via protocol (GCP2-001c)
- Consider how to handle multi-turn consent flows
- Tool descriptions are critical - they guide Copilot behavior
