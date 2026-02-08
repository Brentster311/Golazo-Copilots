# GCP-0025 Design Document: Replace DoR/DoD with Role-Based Output Validation

## Summary

Replace the `gcp_mark_dor` and `gcp_mark_dod` MCP tools with automatic validation of required outputs defined in role files. When an agent attempts to transition to a new role, the system validates that the current role's required outputs exist before allowing the transition.

## Problem Statement

The current DoR/DoD marking system has several issues:

1. **Evidence friction** - Agents must provide evidence in specific formats, leading to infinite loops when validation fails
2. **Redundant tracking** - DoR/DoD checklists duplicate what role files already define as outputs
3. **Fabrication risk** - Agents can fabricate evidence strings without actual verification
4. **Complexity** - Two separate tools (mark_dor, mark_dod) with overlapping purposes

## Business Case

### Why Now
- Active development is being blocked by evidence validation bugs
- Multiple sessions wasted debugging evidence format issues
- Simplification enables faster iteration on the Golazo workflow

### Impact
- Reduce MCP tool count from 7 to 5
- Eliminate evidence-related infinite loops
- Single source of truth (role files) for required outputs

### KPIs
- Zero evidence-related tool failures
- Faster transition cycle time
- Fewer consent/force bypasses needed

## Stakeholders

| Stakeholder | Interest |
|-------------|----------|
| AI Agents (Copilot) | Primary user of MCP tools |
| Human Developers | Observe workflow via status, can force bypass |
| Project Owner | Defines acceptance criteria in user stories |

## Functional Requirements

### FR1: Remove gcp_mark_dor and gcp_mark_dod
- Delete tools from server.py
- Delete tools from gcp_mark.py
- Delete evidence.py module
- Update tests

### FR2: Role files define required outputs
New markdown section in each role file:

```markdown
## Required Outputs
<!-- Validated before transitioning OUT of this role -->
- file: WorkItems/{id}/{id}-User-Story.md
- file: WorkItems/{id}/RoleDecisionNotes/{id}-project-owner-assistant.md
```

### FR3: Transition validates outputs
Before `gcp_transition` allows moving to a new role:
1. Load current role file
2. Parse `## Required Outputs` section
3. Validate each output exists
4. Block transition if any missing, list what's missing
5. Allow `force=True` with prior consent to bypass

### FR4: Status shows output validation
`gcp_status` response includes:

```
**Required Outputs for [current-role]:**
- [x] WorkItems/GCP-0025/GCP-0025-User-Story.md
- [ ] WorkItems/GCP-0025/RoleDecisionNotes/GCP-0025-project-owner-assistant.md
```

### FR5: Validation types

| Type | Syntax | Validation |
|------|--------|------------|
| File | `file: <path>` | Path.exists() and is_file() |
| Directory | `dir: <path>` | Path.exists() and is_dir() |
| Git branch | `git-branch: <pattern>` | `git branch --list <pattern>` |
| Git commit | `git-log: <pattern>` | `git log --oneline --grep=<pattern>` |

Path supports `{id}` placeholder replaced with work item ID.

## Non-Functional Requirements

- Validation < 2 seconds per transition
- Clear error messages with expected paths
- Backward compatible state.json loading (ignore old dor/dod fields)

## Proposed Approach

### Phase 1: Add output validation to role files
1. Update all role files with `## Required Outputs` section
2. Create `output_validator.py` with parsing and validation logic
3. Unit tests for output validation

### Phase 2: Integrate with gcp_transition
1. Call output validator before allowing transition
2. Add output status to gcp_status response
3. Integration tests

### Phase 3: Remove DoR/DoD tools
1. Delete gcp_mark_dor, gcp_mark_dod from server.py
2. Delete evidence.py
3. Remove dor/dod from state.json schema (keep for backward compat loading)
4. Update copilot-instructions.md
5. Delete obsolete tests, update remaining tests

## Alternatives Considered

| Alternative | Rejected Because |
|-------------|-----------------|
| Keep evidence parameter, fix validation | Still has fabrication risk, adds friction |
| Auto-mark on file creation (hooks) | Complex, requires file watching |
| Remove all gates | Loses workflow guardrails |

## Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Role file parsing errors | Medium | High | Strict format, validation tests |
| Git commands fail | Low | Medium | Graceful fallback, clear error messages |
| Breaking existing workflows | High | Medium | v3.0.0 major version, migration docs |

## Open Questions

1. ~~Should we keep dor/dod in state.json for audit trail?~~ No, simplify.
2. ~~What happens to in-flight work items?~~ Transition normally, old dor/dod ignored.

## Dependencies

- None (self-contained refactor)

## Migration / Rollout Plan

1. Implement in feature branch
2. Update version to 3.0.0
3. Update copilot-instructions.md template
4. Deploy to Azure Artifacts
5. Update existing workspaces to new copilot-instructions.md

## Rollback Plan

- Revert to v2.16.7 if issues discovered
- Re-add dor/dod tools if needed (code in git history)

## Observability Plan

- MCP server logs validation results
- gcp_status shows current validation state

## Test Strategy

| Test Type | Coverage |
|-----------|----------|
| Unit tests | output_validator.py parsing, each validation type |
| Integration tests | gcp_transition with valid/invalid outputs |
| Regression tests | Existing transition tests still pass |
