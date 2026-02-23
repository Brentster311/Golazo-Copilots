# Golazo Copilot V2: System Architecture Overview

**Document**: Technical Overview for Project Owner  
**Version**: 2.106.0  
**Last Updated**: February 2026  
**Purpose**: Understand how Golazo Copilot V2 components fit together

---

## Executive Summary

Golazo Copilot V2 is a **Python MCP (Model Context Protocol) server** that enforces a structured 10-role software development workflow through GitHub Copilot. The system provides:

- **7 MCP tools** for workflow management
- **Persistent JSON state** per work item with atomic writes
- **10-role sequential workflow** with gate enforcement
- **Subagent orchestration** — delegates creative work to isolated subagents per role
- **Capability registry** for impact analysis via `capabilities.yaml`
- **Self-contained role context bundles** for stateless subagent delegation

The package is published to Azure Artifacts as `golazo-copilot` and installed via `pip`.

---

## System Architecture

### Layer Diagram

```
+=========================================================================+
|                         USER INTERACTION LAYER                          |
+=========================================================================+
|                                                                         |
|                        +---------------------------+                    |
|                        |    GitHub Copilot          |                    |
|                        |    Chat Interface          |                    |
|                        +---------------------------+                    |
|                                    |                                    |
+=========================================================================+
|                         MCP SERVER LAYER                                |
+=========================================================================+
|                                    |                                    |
|   +-------------------------------------------------------------+       |
|   |                      MCP Server (server.py)                 |       |
|   |                                                             |       |
|   |   Workflow Tools:              Query Tools:                 |       |
|   |   - gcp_create_workitem        - gcp_status                 |       |
|   |   - gcp_transition             - gcp_capabilities           |       |
|   |   - gcp_consent                - gcp_role_context           |       |
|   |   - gcp_bootstrap                                           |       |
|   |                                                             |       |
|   |   Entry point: golazo-copilot = golazo_copilot.server:run   |       |
|   +-------------------------------------------------------------+       |
|                              |                                          |
+=========================================================================+
|                         BUSINESS LOGIC LAYER                            |
+=========================================================================+
|                              |                                          |
|   +-------------------------------------------------------------+       |
|   |                   Transition Engine                         |       |
|   |                                                             |       |
|   |   - Forward: strict sequential (no skipping)                |       |
|   |   - Backward: allowed to any earlier role                   |       |
|   |   - Gates: role notes + required outputs must exist         |       |
|   |   - Force bypass: requires prior gcp_consent record         |       |
|   +-------------------------------------------------------------+       |
|                              |                                          |
|   +-------------------------------------------------------------+       |
|   |                   Consent Enforcement                       |       |
|   |                                                             |       |
|   |   - Records deviations with auto-ID (dev-001, dev-002...)   |       |
|   |   - Actions: skip_outputs, skip_role, revert_progress       |       |
|   |   - Consent consumed on use (single-use tokens)             |       |
|   +-------------------------------------------------------------+       |
|                              |                                          |
|   +-------------------------------------------------------------+       |
|   |                   Output Validator                          |       |
|   |                                                             |       |
|   |   - Parses "## Required Outputs" from role markdown         |       |
|   |   - Types: file, dir, git-branch, git-log                   |       |
|   |   - Validates existence on disk/git before transition        |       |
|   +-------------------------------------------------------------+       |
|                              |                                          |
|   +-------------------------------------------------------------+       |
|   |                   Role Context Bundler                      |       |
|   |                                                             |       |
|   |   - Assembles self-contained context for subagents          |       |
|   |   - Reads YAML front-matter (inputs/outputs/tools)          |       |
|   |   - 100KB max bundle with proportional truncation            |       |
|   +-------------------------------------------------------------+       |
|                              |                                          |
|   +-------------------------------------------------------------+       |
|   |                   Capability Registry                       |       |
|   |                                                             |       |
|   |   - Loads capabilities.yaml                                 |       |
|   |   - BFS transitive impact analysis                          |       |
|   |   - File-to-capability mapping                              |       |
|   +-------------------------------------------------------------+       |
|                              |                                          |
+=========================================================================+
|                         DATA LAYER                                      |
+=========================================================================+
|                              |                                          |
|   +-------------------------------------------------------------+       |
|   |                   State Persistence                         |       |
|   |                                                             |       |
|   |   - JSON file storage per work item (Pydantic models)       |       |
|   |   - Atomic writes: temp file + os.replace()                 |       |
|   |   - Schema version: 1.0                                     |       |
|   |   - ConfigDict(extra="ignore") for forward compat           |       |
|   +-------------------------------------------------------------+       |
|                              |                                          |
|   +-------------------------------------------------------------+       |
|   |                       File System                           |       |
|   |                                                             |       |
|   |   WorkItems/                                                |       |
|   |   +-- GCP-0014/                                             |       |
|   |   |   +-- state.json                                        |       |
|   |   |   +-- GCP-0014-User-Story.md                            |       |
|   |   |   +-- Design/                                           |       |
|   |   |   |   +-- GCP-0014-design-doc.md                        |       |
|   |   |   |   +-- GCP-0014-Review-Comments.md                   |       |
|   |   |   |   +-- GCP-0014-Test-Cases.md                        |       |
|   |   |   +-- RoleDecisionNotes/                                |       |
|   |   |       +-- GCP-0014-program-manager.md                   |       |
|   |   |       +-- GCP-0014-developer.md                         |       |
|   |   |       +-- ...                                           |       |
|   |   +-- GCP-0015/                                             |       |
|   |       +-- state.json                                        |       |
|   |       +-- ...                                               |       |
|   +-------------------------------------------------------------+       |
|                                                                         |
+=========================================================================+
```

---

## MCP Tools (7 Registered)

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| **gcp_create_workitem** | Create a new work item with initial state | `work_item_id`, `profile` (complete/express/spike) |
| **gcp_transition** | Move to the next (or previous) role | `work_item_id`, `role`, `force` |
| **gcp_status** | Comprehensive status with parallel I/O | `work_item_id` (optional — omit for version only) |
| **gcp_bootstrap** | Deploy spine, roles, capabilities to workspace | `force`, `include_roles` |
| **gcp_consent** | Record deviation consent (consumed by transition) | `work_item_id`, `action`, `reason` (min 10 chars) |
| **gcp_capabilities** | Query capability registry | `action` (list/show/impact/validate) |
| **gcp_role_context** | Assemble self-contained context bundle for subagent | `work_item_id`, `role` (defaults to current) |

All tools require `workspace_path` to locate the `WorkItems/` directory.

---

## 10-Role Sequential Workflow

### Role Progression

```
  DEFINITION PHASE              DEVELOPMENT PHASE        COMPLETION PHASE
  ─────────────────             ─────────────────        ────────────────
  1. project-owner-assistant    6. developer             8. documenter
  2. program-manager            7. refactor-expert       9. builder
  3. domain-expert                                      10. retrospective
  4. quality-assurance
  5. architect
```

### Transition Rules

| Rule | Behavior |
|------|----------|
| **Forward** | Strictly sequential — no skipping roles |
| **Backward** | Allowed to any earlier role (always valid) |
| **Same role** | No-op success |
| **Gate: role notes** | Role decision notes file must exist for current role |
| **Gate: required outputs** | Files declared in `## Required Outputs` must exist on disk |
| **Force bypass** | Requires prior `gcp_consent` record; consent is consumed on use |

### Workflow Profiles

| Profile | Description |
|---------|-------------|
| `complete` | Full 10-role workflow (default) |
| `express` | Reduced gates for small changes |
| `spike` | Minimal process for exploration |

Profile is stored in state; all roles are currently traversed regardless of profile.

---

## Component Relationships

```
                    +-------------------+
                    |   GitHub Copilot  |
                    +-------------------+
                              |
                    +-------------------+
                    |    MCP Server     |--- gcp_bootstrap --> .github/
                    +-------------------+
                              |
           +------------------+------------------+
           |                  |                  |
    +-----------+      +-----------+      +-----------+
    | Transition|      |  Status   |      |   Role    |
    |  Engine   |      | (parallel)|      |  Context  |
    +-----------+      +-----------+      |  Bundler  |
           |                              +-----------+
    +-----------+                               |
    |  Consent  |                         +-----------+
    | Enforcement|                        |   Role    |
    +-----------+                         |  Loader   |
           |                              +-----------+
    +-----------+                               |
    |  Output   |                         +-----------+
    | Validator |                         | .github/  |
    +-----------+                         | roles/*.md|
           |                              +-----------+
    +-----------+
    |   State   |
    |Persistence|
    +-----------+
           |
    +-----------+
    |state.json |
    +-----------+
```

---

## Subagent Orchestration

The default operating mode delegates each role's creative work to an isolated subagent:

### Orchestrator Loop

```
For each role in the workflow:
  1. gcp_status(work_item_id)       → current state, progress, version
  2. gcp_role_context(work_item_id) → self-contained context bundle
  3. runSubagent(prompt=bundle)     → subagent executes role work
  4. Verify required outputs exist
  5. gcp_transition(next_role)      → advance (gates enforced)
  6. Display between-role summary
  7. Repeat
```

### Subagent Contract

| Subagent MUST | Subagent MUST NOT |
|---------------|-------------------|
| Create all Required Outputs | Call `gcp_transition` |
| Follow role instructions | Ask user questions |
| Return a summary of work done | Modify `state.json` directly |

### Context Bundle Contents (gcp_role_context)

| Section | Source | Truncatable? |
|---------|--------|-------------|
| Role instructions | `.github/roles/{role}.md` with YAML front-matter | No |
| State summary | Current role, phase, history, deviations | No |
| Input artifacts | Resolved from YAML `inputs:` paths | Yes (proportional) |
| Previous role notes | Prior role's decision notes | Yes (proportional) |

**Size limit**: 100KB max, proportional truncation of artifacts when exceeded.

### Fallback Mode

If subagents are unavailable, the orchestrator switches to **inline execution** (same agent does the work directly). Users can toggle with "work inline" / "use subagents" commands.

---

## Sequence Diagram: Typical Workflow Session

```
User           Copilot        MCP Server     Transition     State
 |                |                |             |             |
 | "Start item"   |                |             |             |
 |--------------->|                |             |             |
 |                | gcp_create_    |             |             |
 |                | workitem()     |             |             |
 |                |--------------->|             |             |
 |                |                | validate_id |             |
 |                |                | create_state|             |
 |                |                |------------------------------>|
 |                |                |             |   state.json |
 |                |                |<------------------------------|
 |                | "Created,      |             |             |
 |                |  role=POA"     |             |             |
 |                |<---------------|             |             |
 |                |                |             |             |
 |                | gcp_role_      |             |             |
 |                | context()      |             |             |
 |                |--------------->|             |             |
 |                |   [bundle]     |             |             |
 |                |<---------------|             |             |
 |                |                |             |             |
 |                | runSubagent    |             |             |
 |                | (POA work)     |             |             |
 |                |----+           |             |             |
 |                |    | creates   |             |             |
 |                |    | User-Story|             |             |
 |                |<---+           |             |             |
 |                |                |             |             |
 |                | gcp_transition |             |             |
 |                | ("program-     |             |             |
 |                |  manager")     |             |             |
 |                |--------------->|             |             |
 |                |                | validate    |             |
 |                |                |------------>|             |
 |                |                | check notes |             |
 |                |                | check outputs             |
 |                |                |   (approved)|             |
 |                |                |<------------|             |
 |                |                | save_state  |             |
 |                |                |------------------------------>|
 |                | "Transitioned  |             |             |
 |                |  to prog-mgr"  |             |             |
 |                |<---------------|             |             |
 |                |                |             |             |
 |                | [repeat for    |             |             |
 |                |  each role...] |             |             |
```

---

## State Model (Pydantic)

### WorkItemState

| Field | Type | Description |
|-------|------|-------------|
| `schema_version` | `Literal["1.0"]` | Always "1.0" |
| `work_item_id` | `str` | ID matching `[A-Za-z]{1,4}-\d{3,}` |
| `profile` | `Literal["complete","express","spike"]` | Workflow profile |
| `current_phase` | `Literal["definition","development","completion"]` | Current phase |
| `current_role` | `str` | Active role name |
| `created_at` | `datetime` | UTC creation timestamp |
| `updated_at` | `datetime` | UTC last-modified timestamp |
| `role_history` | `list[RoleHistoryEntry]` | Ordered entry/exit records |
| `deviations` | `list[Deviation]` | Consent/deviation records |

**Note**: `ConfigDict(extra="ignore")` — legacy fields (e.g., old `dor`/`dod` dicts) are silently ignored on load.

### State File Example

```json
{
  "schema_version": "1.0",
  "work_item_id": "GCP-0014",
  "profile": "complete",
  "current_phase": "development",
  "current_role": "developer",
  "created_at": "2026-01-31T10:00:00Z",
  "updated_at": "2026-01-31T14:30:00Z",
  "role_history": [
    {"role": "project-owner-assistant", "entered_at": "2026-01-31T10:00:00Z", "exited_at": "2026-01-31T10:30:00Z"},
    {"role": "program-manager", "entered_at": "2026-01-31T10:30:00Z", "exited_at": "2026-01-31T11:00:00Z"},
    {"role": "domain-expert", "entered_at": "2026-01-31T11:00:00Z", "exited_at": "2026-01-31T11:20:00Z"},
    {"role": "quality-assurance", "entered_at": "2026-01-31T11:20:00Z", "exited_at": "2026-01-31T12:00:00Z"},
    {"role": "architect", "entered_at": "2026-01-31T12:00:00Z", "exited_at": "2026-01-31T13:00:00Z"},
    {"role": "developer", "entered_at": "2026-01-31T13:00:00Z", "exited_at": null}
  ],
  "deviations": [
    {
      "id": "dev-001",
      "action": "skip_outputs",
      "reason": "exploring architecture, no formal design doc needed",
      "role": "architect",
      "timestamp": "2026-01-31T12:55:00Z",
      "consumed": true,
      "consumed_at": "2026-01-31T13:00:00Z"
    }
  ]
}
```

---

## Package Structure

```
golazo-copilot/
├── pyproject.toml                       # hatchling build, version 2.106.0
├── README.md
├── capabilities.yaml                    # Deployed capability registry
├── .github/roles/                       # Workspace-deployed role overrides
│   ├── architect.md
│   ├── builder.md
│   ├── developer.md
│   ├── documenter.md
│   ├── domain-expert.md
│   ├── program-manager.md
│   ├── project-owner-assistant.md
│   ├── quality-assurance.md
│   ├── refactor-expert.md
│   ├── retrospective.md
│   └── TechBestPractices.md
├── src/golazo_copilot/
│   ├── __init__.py                      # __version__ via importlib.metadata
│   ├── server.py                        # MCP server entry point (7 tools, 7 formatters)
│   ├── bootstrap-instructions.md        # Spine template → .github/copilot-instructions.md
│   ├── capabilities-template.yaml       # Template for capabilities.yaml
│   ├── core/
│   │   ├── __init__.py
│   │   ├── types.py                     # Pydantic models (WorkItemState, etc.)
│   │   ├── state.py                     # State creation & validation
│   │   ├── persistence.py               # Atomic JSON read/write
│   │   ├── transitions.py               # Transition matrix, phase map, validation
│   │   └── output_validator.py          # Required Outputs parser & validator
│   ├── roles/
│   │   ├── __init__.py
│   │   ├── loader.py                    # Local override → package default loading
│   │   └── defaults/                    # 10 role files + TechBestPractices.md
│   └── tools/
│       ├── __init__.py
│       ├── gcp_create_workitem.py
│       ├── gcp_transition.py
│       ├── gcp_status.py                # Parallel I/O via asyncio.gather
│       ├── gcp_bootstrap.py
│       ├── gcp_consent.py
│       ├── gcp_capabilities.py          # BFS impact analysis
│       └── gcp_role_context.py          # Subagent context bundle assembly
└── tests/                               # 18 test files, 391 tests
    ├── test_gcp_create_workitem.py
    ├── test_gcp_transition.py
    ├── test_gcp_status.py
    ├── test_gcp_bootstrap.py
    ├── test_gcp_consent.py
    ├── test_gcp_capabilities.py
    ├── test_output_validator.py
    ├── test_output_integration.py
    ├── test_server_formatters.py
    ├── test_subagent_integration.py
    ├── test_role_self_contained.py
    ├── test_gcp_status_parallel.py
    └── ... (18 total)
```

---

## Configuration: Package vs Workspace

```
+-------------------------------------------------------------------------+
|                     UNIVERSAL (pip install golazo-copilot)              |
|                                                                         |
|   core/transitions.py  -> Transition matrix, validation logic           |
|   core/persistence.py  -> Atomic state read/write                       |
|   core/types.py        -> Pydantic state models                         |
|   tools/*.py           -> 7 MCP tool implementations                    |
|   roles/defaults/*.md  -> Bundled default role instructions             |
|   bootstrap-instructions.md -> Spine template                           |
|                                                                         |
|   VERSIONED * PUBLISHED TO AZURE ARTIFACTS * SAME FOR EVERYONE          |
+-------------------------------------------------------------------------+
                                    |
                                    | deploys via gcp_bootstrap
                                    v
+-------------------------------------------------------------------------+
|                     PER-WORKSPACE (checked into repo)                   |
|                                                                         |
|   .github/copilot-instructions.md  <- Spine (from bootstrap template)  |
|   .github/roles/*.md               <- Role files (overridable locally)  |
|   capabilities.yaml                <- Capability registry               |
|   WorkItems/<id>/state.json        <- Persistent work item state        |
|                                                                         |
|   CUSTOMIZABLE * LOCAL OVERRIDES * PER-TEAM CONFIGURATION               |
+-------------------------------------------------------------------------+
```

### Role File Loading Priority

1. `.github/roles/{role}.md` (workspace local override) — checked first
2. Package default at `roles/defaults/{role}.md` — fallback

### What Retrospective Can Change

| Target | Mechanism | Location |
|--------|-----------|----------|
| Clarify role guidance | Markdown edit | `.github/roles/*.md` |
| Update capabilities | YAML edit | `capabilities.yaml` |
| Modify spine behavior | Edit deployed copy | `.github/copilot-instructions.md` |
| Fix core logic bug | **New package version** | `pip install golazo-copilot==X.Y.Z` |

---

## Bootstrap: What Gets Deployed

When `gcp_bootstrap` runs, it creates:

| File | Source | Purpose |
|------|--------|---------|
| `.github/copilot-instructions.md` | `bootstrap-instructions.md` template | Spine — loaded by GitHub Copilot automatically |
| `.github/roles/*.md` (11 files) | `roles/defaults/` | Role instructions with YAML front-matter |
| `WorkItems/.gitkeep` | Created | Ensures WorkItems directory exists |
| `capabilities.yaml` | `capabilities-template.yaml` | Capability registry |

**Workspace marker validation**: At least one of `pyproject.toml`, `package.json`, `Cargo.toml`, `.hg`, or `WorkItems/` must exist.

---

## Key Workflows

### 1. Starting a New Work Item

```
User: "Start GCP-0053"
  |
  +-> MCP: gcp_create_workitem(work_item_id="GCP-0053", profile="complete")
  |     |
  |     +-> validate_work_item_id() -> matches [A-Za-z]{1,4}-\d{3,}
  |     +-> create_initial_state() -> WorkItemState Pydantic model
  |     +-> save_state() -> WorkItems/GCP-0053/state.json (atomic write)
  |     +-> load_role_instructions("project-owner-assistant")
  |     |
  |     +-> Returns: success + role instructions
  |
  +-> Copilot: Begins orchestrator loop at project-owner-assistant
```

### 2. Transitioning Roles (with Gate Enforcement)

```
Copilot: gcp_transition(work_item_id="GCP-0053", role="program-manager")
  |
  +-> load_state() -> WorkItemState
  +-> validate_transition("project-owner-assistant" -> "program-manager")
  |     +-> Forward: is next in ROLE_ORDER? -> Yes
  +-> Check role decision notes exist on disk
  +-> Check required outputs from role markdown
  |     +-> output_validator.parse() -> list of expected files
  |     +-> output_validator.validate() -> all exist? -> Yes
  +-> Update role_history (exit current, enter new)
  +-> save_state() -> atomic write
  +-> Returns: "Transitioned to program-manager" + role instructions
```

### 3. Forced Transition (with Consent)

```
Copilot: gcp_transition(..., role="developer", force=True)
  |
  +-> validate_transition() -> blocked (missing outputs)
  +-> has_valid_consent("skip_outputs") -> True (from prior gcp_consent call)
  +-> consume_consent() -> marks deviation as consumed
  +-> Transition proceeds
  +-> save_state()
```

### 4. Subagent Delegation

```
Copilot: gcp_role_context(work_item_id="GCP-0053", role="developer")
  |
  +-> load_role_instructions("developer") -> markdown with YAML front-matter
  +-> Parse front-matter: inputs, outputs, tools
  +-> Resolve {id} placeholders in artifact paths
  +-> Read input artifacts from disk (within 100KB budget)
  +-> Read previous role notes (architect notes)
  +-> Assemble markdown bundle:
  |     ## Role Instructions
  |     ## Current State
  |     ## Input Artifacts
  |     ## Previous Role Notes
  +-> Returns: self-contained context string
  |
Copilot: runSubagent(prompt=bundle)
  +-> Subagent executes developer work autonomously
  +-> Returns summary
```

---

## Architectural Philosophy: Deterministic vs Non-Deterministic

### The Core Insight

Golazo Copilot V2 cleanly separates **what can be computed** from **what requires judgment**:

```
+-------------------------------------------------------------------------+
|                    DETERMINISTIC (MCP/Python)                           |
|                                                                         |
|   * Can I transition?        -> Yes/No (transition matrix)              |
|   * Do required outputs exist? -> True/False (file system check)        |
|   * What role am I in?       -> "developer" (state.json lookup)         |
|   * Record deviation         -> Appends to deviations[] (side effect)   |
|   * What context does a role need? -> Bundle from front-matter          |
|                                                                         |
|   TESTABLE * PREDICTABLE * AUDITABLE (391 tests)                        |
+-------------------------------------------------------------------------+
                                    |
                                    | gates & state
                                    v
+-------------------------------------------------------------------------+
|                   NON-DETERMINISTIC (Copilot/LLM/Subagents)             |
|                                                                         |
|   * Write the user story     -> Creative output (POA subagent)          |
|   * Design the solution      -> Architecture (Architect subagent)       |
|   * Implement the feature    -> Code generation (Developer subagent)    |
|   * Review for quality       -> Judgment call (QA subagent)             |
|                                                                         |
|   CREATIVE * CONTEXTUAL * NUANCED                                       |
+-------------------------------------------------------------------------+
                                    |
                                    | guidance
                                    v
+-------------------------------------------------------------------------+
|                      SPINE (.github/copilot-instructions.md)            |
|                                                                         |
|   * Forbidden actions list                                              |
|   * Orchestrator loop template                                          |
|   * Subagent prompt template                                            |
|   * Between-role summary format                                         |
|   * File naming conventions                                             |
|   * Fallback mode instructions                                          |
|                                                                         |
|   REFERENCE * ROUTING * CONVENTIONS (~137 lines)                        |
+-------------------------------------------------------------------------+
```

### What Goes Where

| Concern | Enforcement | Mechanism |
|---------|-------------|-----------|
| "Can I go to developer?" | Code | `transitions.validate_transition()` |
| "Do outputs exist?" | Code | `output_validator.validate()` |
| "Record this skip" | Code | `gcp_consent()` → `deviations[]` |
| "What role am I in?" | Code | `state.json` → `current_role` |
| "How to write this design" | Role file | `.github/roles/architect.md` |
| "Use subagents by default" | Spine | `bootstrap-instructions.md` |

### Why This Matters

| Problem | Solution |
|---------|----------|
| LLM ignores/forgets rules | MCP tool returns blocked + reason |
| No audit trail | `deviations[]` persisted in state.json |
| State lost between sessions | Persistent JSON files with atomic writes |
| Can't test workflow logic | 391 pytest tests across 18 files |
| Context too large for one agent | Role context bundler with 100KB limit |
| Creative work quality varies | Isolated subagents with focused context |

**Result**: Hard enforcement for *when* things can happen + soft guidance for *how* to do things well + isolated context for *who* does each piece.

---

## Version History

| Version | Key Changes |
|---------|-------------|
| 2.106.0 | Subagent orchestration spine, role context bundler, handoff protocol, parallel status I/O, self-contained roles |
| 2.105.x | Role improvements, domain expert enhancements, workspace path handling |
| 2.102.0 | Version comment standardization, stale file detection, capability registry |
| 2.100.x | Initial V2 release — MCP server, 7 tools, 10 roles, persistent state |

---

## Further Reading

- **Work item artifacts**: `WorkItems/GCP-NNNN/` for design docs, test cases, and role notes
- **Subagent protocol**: `WorkItems/Golazo-Subagent-Handoff-Protocol.md`
- **Capability registry**: `capabilities.yaml` at workspace root
- **Role files**: `.github/roles/*.md` for per-role instructions with YAML front-matter
