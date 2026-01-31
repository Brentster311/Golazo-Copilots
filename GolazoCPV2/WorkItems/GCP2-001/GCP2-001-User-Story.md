# GCP2-001: Agent-Based Architecture (Epic)

**Status**: Draft  
**Priority**: High  
**Created**: 2026-01-27  
**Updated**: 2026-01-27  
**Type**: Epic

## Overview

This epic covers the foundational Golazo V2 agent that enforces workflow through code rather than prompt engineering.

## Sub-Stories

| ID | Title | Scope | Priority |
|----|-------|-------|----------|
| **GCP2-001a** | Core State Machine | State transitions, DoR/DoD validation | High |
| **GCP2-001b** | Consent-Based Enforcement | Skip detection, clarification, audit logging | High |
| **GCP2-001c** | Golazo Protocol + CLI | JSON-RPC protocol, CLI commands | High |
| **GCP2-001d** | Copilot/MCP Integration | MCP tools for Copilot integration | High |

## Implementation Order

```
GCP2-003 (State Schema)
    ?
GCP2-001a (Core State Machine)
    ?
GCP2-001b (Consent Enforcement)
    ?
GCP2-001c (Protocol + CLI)
    ?
GCP2-001d (Copilot/MCP)
```

---

## User Story

**As a** developer using Golazo Copilot V2,  
**I want** the workflow to be enforced by a programmatic agent rather than prompt engineering alone,  
**So that** state machine enforcement is reliable, consistent, and not dependent on Copilot "remembering" workflow state.

## Background

Golazo V1 relies entirely on markdown-based instructions that Copilot must interpret and follow. This approach has limitations:
- State tracking depends on Copilot parsing status headers
- Copilot autonomously skips steps without user permission
- No programmatic validation of DoR/DoD conditions
- No audit trail of workflow deviations

### The Core Problem

V1's enforcement is "advisory" — Copilot often decides on its own to skip roles, especially when it perceives a task as "simple." This is problematic because:

| Behavior | Problem |
|----------|---------|
| Copilot skips Architect for "simple" changes | Copilot's judgment of simplicity is unreliable |
| Copilot skips Tester because "tests aren't needed" | Defeats TDD discipline |
| Copilot jumps to Developer without DoR | Produces code without proper design |

**However**, there are legitimate cases where skipping is appropriate — but only when the **user explicitly requests it**.

## Enforcement Philosophy: Consent-Based

V2 adopts **consent-based enforcement**:

| Scenario | Agent Behavior |
|----------|----------------|
| User says nothing about workflow | ? **Strict** - follow all roles in sequence |
| User says "skip the design phase" | ? **Allow** - user explicitly consented |
| User says "just fix this quickly" | ?? **Clarify** - ask if they want Express profile |
| Copilot thinks "this is simple" | ? **Block** - no autonomous skipping |
| User selected Express profile | ? **Allow** - pre-consented to reduced workflow |

### What Counts as Explicit Consent?

The agent recognizes explicit skip requests such as:
- "Skip the Architect role"
- "I don't need a design doc for this"
- "Fast-track this" / "Express mode"
- "Just write the code" (triggers clarification)
- Selecting a reduced workflow profile (GCP2-002)

The agent does **NOT** infer consent from:
- Task appearing "simple"
- Small number of files changed
- User not mentioning a role
- Time pressure implied in user's message

## Acceptance Criteria

### Core State Machine
1. [ ] Workflow state machine implemented in code (Python)
2. [ ] DoR/DoD conditions validated programmatically before role transitions
3. [ ] Agent maintains state across conversation turns
4. [ ] Clear API for querying current workflow state

### Consent-Based Enforcement
5. [ ] Agent never skips roles autonomously (without user consent)
6. [ ] Agent recognizes explicit skip requests from user
7. [ ] Ambiguous requests (e.g., "just fix it") trigger clarification prompt
8. [ ] All skips require confirmation: "Skipping Architect role as requested. Proceeding to Tester."

### Audit Trail
9. [ ] Every workflow deviation is logged with timestamp
10. [ ] Log includes: who requested (user), what was skipped, why (user's words)
11. [ ] Audit log stored in work item state file
12. [ ] Deviations visible in status queries

### Integration
13. [ ] Agent integrates with Copilot via MCP tools or custom agent framework
14. [ ] Protocol supports IDE extensions (GCP2-005)

## Proposed Skip Audit Schema

```json
{
  "deviations": [
    {
      "timestamp": "2026-01-27T14:30:00Z",
      "type": "role_skipped",
      "role": "architect",
      "requestedBy": "user",
      "reason": "User said: 'skip the design, this is a one-line fix'",
      "approved": true
    }
  ]
}
```

## Agent Response Examples

### User tries to skip without asking
```
User: "Add a null check to the GetUser method"

Agent: "I'll help with that. Currently in Project Owner role.
        
        To proceed, I need to:
        1. Create/update the User Story
        2. Move through Architect ? Tester ? Developer
        
        Would you like to:
        - Follow standard workflow
        - Use Express profile (PO ? Developer ? Builder)
        - Skip specific roles (please specify)"
```

### User explicitly requests skip
```
User: "Skip the design phase and just write the fix"

Agent: "? Skipping Architect role as requested.
        ? Skipping Tester role as requested.
        
        ?? Note: Proceeding without design review or test cases.
        This deviation has been logged.
        
        Moving to Developer role..."
```

### Ambiguous request triggers clarification
```
User: "Just fix this bug quickly"

Agent: "I can help fix this quickly. To clarify:
        
        - **Express mode**: Minimal workflow (PO ? Developer ? Builder)
        - **Standard mode**: Full quality gates
        
        Which would you prefer?"
```

## Out of Scope

- Full IDE plugin development (covered in GCP2-005)
- GitHub Issues integration (covered in GCP2-003)
- Role consolidation decisions (covered in GCP2-002)
- Defining workflow profiles (covered in GCP2-002)

## Dependencies

- None (foundational work item)

## Technical Notes

- Consider leveraging MCP (Model Context Protocol) for tool integration
- Explore Copilot Agent mode capabilities
- State stored in JSON files (see GCP2-003 for schema)
- Consent detection may use keyword matching + LLM interpretation
- "Clarification mode" prevents action until user confirms intent
