# Golazo Copilot V2: System Architecture Overview

**Document**: Technical Overview for Project Owner  
**Version**: 2.0  
**Purpose**: Understand how Golazo Copilot V2 components fit together

---

## Executive Summary

Golazo Copilot V2 transforms the current markdown-instruction-based workflow enforcement into a **programmatic system** with:
- Persistent state tracking
- Automated role transitions
- MCP Server integration for GitHub Copilot
- Multi-session support

---

## System Architecture

### Layer Diagram

```
+=========================================================================+
|                         USER INTERACTION LAYER                          |
+=========================================================================+
|                                                                         |
|                        +---------------------------+                    |
|                        |    GitHub Copilot         |                    |
|                        |    Chat Interface         |                    |
|                        +---------------------------+                    |
|                                    |                                    |
+=========================================================================+
|                         INTEGRATION LAYER                               |
+=========================================================================+
|                                    |                                    |
|   +-------------------------------------------------------------+       |
|   |                         MCP Server                          |       |
|   |                                                             |       |
|   |   Tools:                         Resources:                 |       |
|   |   - gcp_status                   - state://current          |       |
|   |   - gcp_transition               - dor://checklist          |       |
|   |   - gcp_mark_dor                 - dod://checklist          |       |
|   |   - gcp_check_consent                                       |       |
|   +-------------------------------------------------------------+       |
|                              |                                          |
|   +-------------------------------------------------------------+       |
|   |                       CLI Commands                          |       |
|   |                                                             |       |
|   |   gcp status             gcp transition <role>              |       |
|   |   gcp dor                gcp dod                            |       |
|   |   gcp init <id>          gcp consent <action>               |       |
|   +-------------------------------------------------------------+       |
|                              |                                          |
+=========================================================================+
|                         BUSINESS LOGIC LAYER                            |
+=========================================================================+
|                              |                                          |
|   +-------------------------------------------------------------+       |
|   |                   Consent Enforcement                       |       |
|   |                                                             |       |
|   |   - Detects user consent phrases ("yes", "proceed", etc.)   |       |
|   |   - Records deviations with justification                   |       |
|   |   - Enforces "ask before skip" policy                       |       |
|   +-------------------------------------------------------------+       |
|                              |                                          |
|   +-------------------------------------------------------------+       |
|   |                   Core State Machine                        |       |
|   |                                                             |       |
|   |   - Role transition validation                              |       |
|   |   - Phase boundary enforcement (DoR gate)                   |       |
|   |   - DoR/DoD checklist management                            |       |
|   |   - Role history tracking                                   |       |
|   +-------------------------------------------------------------+       |
|                              |                                          |
|   +-------------------------------------------------------------+       |
|   |                   Multi-Session Manager                     |       |
|   |                                                             |       |
|   |   - Switch between active work items                        |       |
|   |   - List all work items with status                         |       |
|   |   - Context preservation on switch                          |       |
|   +-------------------------------------------------------------+       |
|                              |                                          |
|   +-------------------------------------------------------------+       |
|   |                   Workflow Profiles                         |       |
|   |                                                             |       |
|   |   - "complete": Full Golazo Copilot workflow                |       |
|   |   - "express": Reduced gates for small changes              |       |
|   |   - "spike": Minimal process for exploration                |       |
|   +-------------------------------------------------------------+       |
|                              |                                          |
+=========================================================================+
|                         DATA LAYER                                      |
+=========================================================================+
|                              |                                          |
|   +-------------------------------------------------------------+       |
|   |                   State Persistence                         |       |
|   |                                                             |       |
|   |   - JSON file storage per work item                         |       |
|   |   - Atomic writes (corruption protection)                   |       |
|   |   - Schema versioning for migrations                        |       |
|   +-------------------------------------------------------------+       |
|                              |                                          |
|   +-------------------------------------------------------------+       |
|   |                       File System                           |       |
|   |                                                             |       |
|   |   WorkItems/                                                |       |
|   |   +-- feature-a/                                            |       |
|   |   |   +-- state.json          <- Workflow state             |       |
|   |   |   +-- User-Story.md                                     |       |
|   |   |   +-- Design/                                           |       |
|   |   +-- feature-b/                                            |       |
|   |       +-- state.json                                        |       |
|   |       +-- ...                                               |       |
|   +-------------------------------------------------------------+       |
|                                                                         |
+=========================================================================+
```

---

## Component Relationships

```
                    +-------------------+
                    |   GitHub Copilot  |
                    +-------------------+
                              |
                    +-------------------+
                    |    MCP Server     |
                    +-------------------+
                              |
                    +-------------------+
                    |       CLI         |
                    +-------------------+
                              |
                    +-------------------+
                    |     Consent       |
                    +-------------------+
                              |
                    +-------------------+
                    |  State Machine    |
                    +-------------------+
                              |
             +----------------+----------------+
             |                |                |
      +------------+   +------------+   +------------+
      |   Multi-   |   |  Workflow  |   |   State    |
      |  Session   |   |  Profiles  |   | Persistence|
      +------------+   +------------+   +------------+
                                               |
                                        +------------+
                                        | state.json |
                                        +------------+
```

---

## UML Sequence Diagram: Typical Workflow Session

```
User           Copilot        MCP Server     Consent        Machine        State
 |                |                |            |              |              |
 | "Start item"   |                |            |              |              |
 |--------------->|                |            |              |              |
 |                | gcp_init()     |            |              |              |
 |                |--------------->|            |              |              |
 |                |                | create_state              |              |
 |                |                |------------------------------>---------->|
 |                |                |            |              | state.json   |
 |                |                |<------------------------------<----------|
 |                | "Work item     |            |              |              |
 |                |  created"      |            |              |              |
 |                |<---------------|            |              |              |
 |                |                |            |              |              |
 | "Create user   |                |            |              |              |
 |  story"        |                |            |              |              |
 |--------------->|                |            |              |              |
 |                | [Creates       |            |              |              |
 |                |  markdown]     |            |              |              |
 |                | gcp_mark_dor() |            |              |              |
 |                |--------------->|            |              |              |
 |                |                | mark_dor   |              |              |
 |                |                |-------------------------->|              |
 |                |                |            |              | save_state   |
 |                |                |            |              |------------->|
 |                |                |            |              |              |
 | "Move to       |                |            |              |              |
 |  program-mgr"  |                |            |              |              |
 |--------------->|                |            |              |              |
 |                | gcp_transition |            |              |              |
 |                |--------------->|            |              |              |
 |                |                | check_consent             |              |
 |                |                |----------->|              |              |
 |                |                | (approved) |              |              |
 |                |                |<-----------|              |              |
 |                |                | transition |              |              |
 |                |                |-------------------------->|              |
 |                |                |            |              | (validates,  |
 |                |                |            |              |  updates)    |
 |                |                |            |              |------------->|
 |                | "Transitioned  |            |              |              |
 |                |  to prog-mgr"  |            |              |              |
 |                |<---------------|            |              |              |
```

---

## State File Example

After a workflow session, the `state.json` contains:

```json
{
  "schemaVersion": "1.0",
  "workItemId": "user-provided-id",
  "profile": "complete",
  "currentPhase": "development",
  "currentRole": "developer",
  "createdAt": "2026-01-31T10:00:00Z",
  "updatedAt": "2026-01-31T14:30:00Z",
  "dor": {
    "userStory": true,
    "designDoc": true,
    "reviewComments": true,
    "testCases": true
  },
  "dod": {
    "branchCreated": true,
    "testsWrittenFirst": false,
    "testsPass": false,
    "buildPasses": false,
    "docsUpdated": false,
    "refactorComplete": false,
    "committed": false
  },
  "roleHistory": [
    {"role": "project-owner", "enteredAt": "2026-01-31T10:00:00Z", "exitedAt": "2026-01-31T10:30:00Z"},
    {"role": "program-manager", "enteredAt": "2026-01-31T10:30:00Z", "exitedAt": "2026-01-31T11:00:00Z"},
    {"role": "quality-assurance", "enteredAt": "2026-01-31T11:00:00Z", "exitedAt": "2026-01-31T12:00:00Z"},
    {"role": "architect", "enteredAt": "2026-01-31T12:00:00Z", "exitedAt": "2026-01-31T13:00:00Z"},
    {"role": "developer", "enteredAt": "2026-01-31T13:00:00Z", "exitedAt": null}
  ],
  "deviations": [
    {
      "action": "skip_dor",
      "reason": "exploring",
      "role": "architect",
      "timestamp": "2026-01-31T12:55:00Z"
    }
  ]
}
```

---

## Component Dependencies

```
                         Workflow Definition (gcp.yaml)
                                    |
                                    | defines roles/phases
                                    v
+--------------------------------------------------------------------------+
|                                                                          |
|   State           --------->  State Machine  --------->  Consent         |
|   Persistence                                            Enforcement     |
|                                      |                      |            |
|                                      +----------------------+            |
|                                                 |                        |
|                                                 v                        |
|                                           CLI Commands                   |
|                                                 |                        |
|                                                 v                        |
|                                           MCP Server                     |
|                                                                          |
+--------------------------------------------------------------------------+
                                    |
                    +---------------+---------------+
                    |                               |
               Multi-Session                   Workflow Profiles
               (switch work items)             (complete/express/spike)
```

---

## Key Workflows

### 1. Starting a New Work Item

```
User: "Start new feature"
  |
  +-> MCP: gcp_init(work_item_id, profile="complete")
  |     |
  |     +-> StateMachine: create(work_item_id)
  |     |     |
  |     |     +-> State: create_state() -> state.json created
  |     |
  |     +-> Returns: "Work item created, starting at project-owner"
  |
  +-> Copilot: Displays status header, begins Project Owner role
```

### 2. Transitioning Roles

```
User: "Move to program-manager"
  |
  +-> MCP: gcp_transition("program-manager")
  |     |
  |     +-> Consent: check_consent(user_message) -> True
  |     |
  |     +-> StateMachine: can_transition("program-manager") -> (True, "allowed")
  |     |
  |     +-> StateMachine: transition("program-manager")
  |     |     |
  |     |     +-> Updates roleHistory
  |     |     +-> State: save_state()
  |     |
  |     +-> Returns: "Transitioned to program-manager"
  |
  +-> Copilot: Loads Program Manager role instructions, continues
```

### 3. DoR Gate Enforcement

```
User: "Move to developer" (DoR incomplete)
  |
  +-> MCP: gcp_transition("developer")
  |     |
  |     +-> StateMachine: can_transition("developer")
  |     |     |
  |     |     +-> is_dor_complete() -> False
  |     |
  |     +-> Returns: (False, "DoR must be complete before Development")
  |
  +-> Copilot: "Cannot proceed. Missing: testCases"
  |
  +-> User can either:
        +-> Complete the missing items
        +-> Request deviation with justification
```

### 4. Recording a Deviation

```
User: "Skip DoR, I'm just exploring"
  |
  +-> MCP: gcp_consent("skip_dor", reason="exploring")
  |     |
  |     +-> Consent: record_deviation(action, reason)
  |     |     |
  |     |     +-> State: append to deviations[], save()
  |     |
  |     +-> Returns: "Deviation recorded"
  |
  +-> MCP: gcp_transition("developer", force=True)
  |     |
  |     +-> StateMachine: transition() with consent override
  |
  +-> Copilot: "Proceeding with deviation recorded"
```

---

## Implementation Components

| Component | Description | Dependencies |
|-----------|-------------|--------------|
| Workflow Definition | Role/phase configuration | None |
| State Persistence | JSON file storage per work item | None |
| Core State Machine | Role transitions, DoR/DoD gates | State Persistence |
| Consent Enforcement | Deviation tracking, approval flow | State Machine |
| Configuration System | gcp.yaml loading | State Machine |
| CLI Commands | Terminal interface | Consent, Config |
| MCP Server | GitHub Copilot integration | CLI |
| Multi-Session | Switch between work items | State Machine |
| Workflow Profiles | complete/express/spike modes | Config |

---

## Configuration vs Code: Separation of Concerns

### The Principle

```
+-------------------------------------------------------------------------+
|                     UNIVERSAL (pip install golazo-copilot)              |
|                                                                         |
|   machine.py    -> Core state machine LOGIC                             |
|   consent.py    -> Consent detection LOGIC                              |
|   state.py      -> Persistence LOGIC                                    |
|   config.py     -> Configuration LOADING                                |
|                                                                         |
|   VERSIONED * PUBLISHED * SAME FOR EVERYONE                             |
+-------------------------------------------------------------------------+
                                    |
                                    | reads
                                    v
+-------------------------------------------------------------------------+
|                     PER-REPO CONFIGURATION (gcp.yaml)                   |
|                                                                         |
|   roles: [project-owner, program-manager, ...]                          |
|   transitions: {project-owner: [program-manager], ...}                  |
|   dor: {items: [userStory, designDoc, ...]}                             |
|   profiles: {complete: {...}, express: {...}}                           |
|                                                                         |
|   CHECKED INTO REPO * PER-TEAM CUSTOMIZATION                            |
+-------------------------------------------------------------------------+
```

### What Retrospective Can Change

| Target | Mechanism | Location |
|--------|-----------|----------|
| Add/remove roles | Config change | `gcp.yaml` |
| Modify transitions | Config change | `gcp.yaml` |
| Change DoR/DoD items | Config change | `gcp.yaml` |
| Clarify role guidance | Markdown change | `.github/roles/*.md` |
| Fix bug in core logic | **PR to golazo-copilot package** | Central repo |

**Retrospective never modifies Python source in user repos.**

---

## Benefits of Golazo Copilot V2 Architecture

| V1 (Current) | V2 (Target) |
|--------------|-------------|
| State in conversation context only | Persistent JSON state files |
| Lost progress on session end | Resume any time |
| No programmatic access | Full API (CLI, MCP) |
| Human enforces workflow | Machine validates transitions |
| No audit trail | Deviations recorded |
| Single work item | Multi-session switching |
| One-size-fits-all | Workflow profiles |

---

## Architectural Philosophy: Deterministic vs Non-Deterministic

### The Core Insight

Golazo Copilot V2 cleanly separates **what can be computed** from **what requires judgment**:

```
+-------------------------------------------------------------------------+
|                    DETERMINISTIC (MCP/Python)                           |
|                                                                         |
|   * Can I transition?        -> Yes/No (computed from transition matrix)|
|   * Is DoR complete?         -> True/False (all items checked)          |
|   * What role am I in?       -> "developer" (state lookup)              |
|   * Record deviation         -> Appends to list (side effect)           |
|                                                                         |
|   TESTABLE * PREDICTABLE * AUDITABLE                                    |
+-------------------------------------------------------------------------+
                                    |
                                    | gates & state
                                    v
+-------------------------------------------------------------------------+
|                   NON-DETERMINISTIC (Copilot/LLM)                       |
|                                                                         |
|   * Write the user story     -> Creative output                         |
|   * Implement this feature   -> Code generation                         |
|   * Review this design       -> Judgment call                           |
|   * Explain why this failed  -> Reasoning                               |
|                                                                         |
|   CREATIVE * CONTEXTUAL * NUANCED                                       |
+-------------------------------------------------------------------------+
                                    |
                                    | guidance
                                    v
+-------------------------------------------------------------------------+
|                      SPINE (Index/Reference)                            |
|                                                                         |
|   * Points to role files:     ".github/roles/developer.md"              |
|   * Coding standards:         "Use existing patterns"                   |
|   * Artifact paths:           "WorkItems/<id>/Design/"                  |
|   * How to call MCP tools:    "Use gcp_status before responding"        |
|                                                                         |
|   REFERENCE * GUIDANCE * CONVENTIONS                                    |
+-------------------------------------------------------------------------+
```

### What Goes Where

| Concern | V1 (Spine enforces) | V2 (Code enforces) |
|---------|---------------------|-------------------|
| "Can I go to developer?" | Prose rules | `machine.can_transition()` |
| "Is DoR complete?" | Checklist prose | `machine.is_dor_complete()` |
| "Record this skip" | (often forgotten) | `consent.record_deviation()` |
| "What role am I in?" | Conversation memory | `state.json` -> `machine.current_role` |
| "How to write good tests" | Role file | Role file *(unchanged)* |
| "Use async/await pattern" | Spine | Spine *(unchanged)* |

### The Spine Becomes a Routing Table

**V1 Spine**: ~500 lines of enforcement rules, checklists, and state machine prose  
**V2 Spine**: ~50 lines pointing to role files, coding standards, and MCP tool usage

The orchestration logic moves from **prose that LLMs may ignore** to **code that blocks invalid actions**.

### Why This Matters

| V1 Problem | V2 Solution |
|------------|-------------|
| LLM ignores/forgets rules | MCP tool returns `(False, "blocked")` |
| No audit trail | `deviations[]` persisted in state.json |
| State lost between sessions | Persistent JSON files |
| Can't test workflow logic | `pytest tests/test_machine.py` |
| Rules duplicated across prose | Single source of truth in Python |

**Result**: Soft guidance for *how* to do things well + hard enforcement for *when* things can happen.

---

## Questions?

This document provides a high-level overview. For details on any specific component, see the individual work item artifacts in `WorkItems/`.
