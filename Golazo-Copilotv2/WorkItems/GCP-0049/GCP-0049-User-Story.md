# GCP-0049 User Story

**Status**: BACKLOG

## User Story

- **Title:** Role Context Bundler MCP Tool
- **As a:** Golazo Copilot user (or orchestrator agent)
- **I want:** A new MCP tool `gcp_role_context` that assembles a minimal, self-contained context package for a specific role — including the role's instructions, relevant work item artifacts, current state summary, and any review feedback from prior roles
- **So that:** An orchestrator agent can call `gcp_role_context(work_item_id, role)` and receive everything a subagent needs to perform that role's work, without the subagent needing access to the full conversation history or unrelated artifacts

- **Out of scope:**
  - Changes to existing MCP tools (gcp_status, gcp_transition, etc.)
  - Subagent spawning logic (that's in the spine / Copilot layer — GCP-0050)
  - Changes to role file content (that's GCP-0048)
  - Multi-work-item orchestration

- **Assumptions:**
  - **Assumption (explicit):** The context bundle is a structured dict returned as formatted markdown text (consistent with other MCP tool responses). It contains: (a) role instructions (full markdown), (b) input artifacts (file contents for artifacts listed in the role's front-matter `inputs:`), (c) state summary (current role, phase, deviation count, relevant history), (d) previous role's decision notes (if they exist)
  - **Assumption (explicit):** The tool reads artifact contents eagerly — it returns the actual file content, not just paths — because subagents may not have filesystem access or may run in a context where reading files costs extra tool calls
  - **Assumption (explicit):** A size guard limits the total bundle to a configurable maximum (default: 100KB) to avoid blowing context windows. If the bundle exceeds the limit, large artifacts are truncated with a `[truncated — full file at <path>]` marker
  - **Assumption (explicit):** The tool uses the YAML front-matter from GCP-0048's role files to determine which artifacts to include. If front-matter is missing (backward compat), it falls back to a hardcoded mapping of role → expected input artifacts

- **Acceptance Criteria (bulleted, testable):**
  - [ ] AC1: `gcp_role_context` is registered in `server.py` as a new MCP tool with parameters `work_item_id` (required), `role` (optional — defaults to current role from state)
  - [ ] AC2: The returned bundle includes sections: `## Role Instructions`, `## Current State`, `## Input Artifacts`, `## Previous Role Notes`
  - [ ] AC3: `## Input Artifacts` contains the actual file content (not just paths) for each artifact listed in the role's front-matter `inputs:` that exists on disk; missing artifacts are listed with `[not yet created]`
  - [ ] AC4: When the total bundle exceeds the size limit (configurable, default 100KB), the largest artifact sections are truncated with a marker pointing to the full file path
  - [ ] AC5: When called without a `role` parameter, the tool uses `current_role` from the work item's state.json
  - [ ] AC6: When called for a role that has no front-matter `inputs:` (backward compat), the tool returns role instructions + state summary without artifact content, and includes a warning
  - [ ] AC7: New test file `test_gcp_role_context.py` covers AC2–AC6 with unit tests
  - [ ] AC8: `capabilities.yaml` is updated with a `tool-role-context` capability entry

- **Non-functional requirements:**
  - Response time under 500ms for a typical work item with 5–10 artifacts
  - Bundle format must be parseable by an LLM without special tooling (plain markdown with clear section headers)

- **Telemetry / metrics expected:** None initially

- **Rollout / rollback notes:**
  - Rollout: Bump version, rebuild package. New tool appears automatically in MCP tool list.
  - Rollback: Remove tool registration from server.py, rebuild.

## Dependencies

- **Depends on:** GCP-0048 (role files need front-matter `inputs:`/`outputs:` for the bundler to read)
- **Prerequisite for:** GCP-0050 (the orchestration spine references this tool), GCP-0052 (integration tests use it)
