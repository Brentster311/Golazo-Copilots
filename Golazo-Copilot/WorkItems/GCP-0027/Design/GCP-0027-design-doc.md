# GCP-0027 Design Document: Remove DoR/DoD Marking Tools and Dead Code Cleanup

## Summary

Remove the obsolete `gcp_mark_dor` and `gcp_mark_dod` MCP tools and the orphaned `evidence.py` module, completing Phase 3 of the GCP-0025 output validation replacement. Additionally fix `gcp_status` to surface `required_outputs` validation results with remediation guidance, and clean up stale bootstrap instructions.

## Problem Statement

1. **Stale bootstrap instructions**: `bootstrap-instructions.md` still documents `gcp_mark_dor`/`gcp_mark_dod` with `evidence=` parameters — tools that no longer exist in the server
2. **Dead code**: `evidence.py` has zero production imports — it was replaced by `output_validator.py` (GCP-0025) but never deleted
3. **Silent data loss in status**: `gcp_status.py` computes `required_outputs` validation results, but `server.py` formatting layer drops them — users never see which outputs are missing or how to fix them
4. **No remediation in next steps**: `_generate_next_steps()` operates purely on old DoR/DoD checklist keys, not on the output validation model

## Business Case

### Why Now
- Bootstrap instructions actively mislead users by documenting removed tools
- `gcp_status` computes validation data that's thrown away — wasted computation with no user benefit
- Dead code creates confusion during maintenance

### Impact
- Clean MCP tool surface: 5 tools, no ghosts
- Status output becomes actionable: shows what's missing AND what to create
- Bootstrap instructions match actual API

### KPIs
- Zero references to `gcp_mark_dor`/`gcp_mark_dod` in entire codebase
- Zero orphaned modules (no production imports = deleted)
- `gcp_status` output includes required outputs with remediation text

## Stakeholders

| Stakeholder | Interest |
|-------------|----------|
| AI Agents (Copilot) | Primary user — reads status, needs actionable next steps |
| Human Developers | Review status output, need to understand what's missing |
| Project Owner | Defines acceptance criteria in user stories |

## Functional Requirements

### FR1: Confirm mark tools are removed
Verify `gcp_mark_dor`, `gcp_mark_dod`, and `gcp_mark.py` are absent from server, tools, and exports. (Already done in prior work — verify no regression.)

### FR2: Delete dead code
- Delete `core/evidence.py` (zero production imports, replaced by `output_validator.py`)
- Delete `tests/test_evidence.py` (tests for dead code)

### FR3: Update bootstrap instructions
- Remove all `gcp_mark_dor`/`gcp_mark_dod` examples and `evidence=` parameter documentation from `bootstrap-instructions.md`
- Ensure the file accurately describes the current 5-tool API with output validation

### FR4: Surface required_outputs in status
- `server.py` formatting must render the `required_outputs` data that `gcp_status.py` already computes
- Show each output with its validation state (exists / missing)

### FR5: Add remediation to next steps
- `_generate_next_steps()` must include remediation actions for missing required outputs
- Format: "Create `<path>` — required output for <role>"
- This replaces/augments the current DoR-key-based "Complete X" messages

## Non-Functional Requirements

- All 121+ existing tests pass (minus intentionally deleted test files)
- No new dependencies
- Breaking change: users on older versions lose `gcp_mark_dor`/`gcp_mark_dod`

## Proposed Approach

### Step 1: Delete dead code
- `rm core/evidence.py`, `rm tests/test_evidence.py`
- Already done in current session — verify

### Step 2: Update bootstrap-instructions.md
- Remove `gcp_mark_dor`/`gcp_mark_dod` sections (lines ~37-52, ~79-85)
- Update version header
- Ensure output validation documentation is accurate

### Step 3: Surface required_outputs in server.py status formatting
- In the `gcp_status` response formatting block (~lines 232-270), render the `required_outputs` field
- Format as checklist: `[x]` or `[ ]` with path

### Step 4: Add remediation to _generate_next_steps in gcp_status.py
- Pass `validation_result` (or `output_specs`) to `_generate_next_steps()`
- For each invalid output, emit: "Create `<path>` — required by <current_role>"
- This makes status actionable

### Step 5: Verify mark tools are absent (regression check)
- `grep` for `gcp_mark`, `mark_dor`, `mark_dod` across source — expect zero hits
- Run test suite — expect 121+ pass

### Step 6: Version bump
- Bump version in `pyproject.toml`

## Alternatives Considered

| Alternative | Rejected Because |
|-------------|-----------------|
| Leave evidence.py as-is | Dead code creates maintenance confusion |
| Skip status remediation | Violates AC #5 — status must show the fix, not just the problem |
| Create separate story for status enhancement | Originally considered, but it's directly tied to "output validation still works" AC |

## Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Bootstrap instructions have other stale content | Medium | Low | Full review during edit |
| Status formatting changes break existing parsing | Low | Medium | Status is human-readable text, not machine-parsed |
| Missing required_outputs in some code paths | Low | Medium | Test status output includes outputs |

## Dependencies

- GCP-0025 (output_validator.py) — already complete
- GCP-0026 (role files with Required Outputs) — already complete

## Migration / Rollout Plan

1. Delete dead code
2. Update bootstrap instructions
3. Fix status output
4. Run tests
5. Bump version
6. Deploy

## Rollback Plan

- Revert to previous version from git history
- `evidence.py` and mark tools remain in git history if needed

## Observability Plan

- `gcp_status` output now shows required outputs validation — observable by user
- MCP server logs validation results during transitions

## Test Strategy

| Test Type | Coverage |
|-----------|----------|
| Regression | All 121+ existing tests pass |
| Deletion verification | `grep` confirms zero references to removed code |
| Status output | Existing `test_gcp_status.py` tests for output validation |
| Integration | `test_output_integration.py` tests transition + status with outputs |
| New test needed | Status next steps include remediation for missing outputs |
