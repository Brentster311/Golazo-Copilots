# GCP-0027: Remove DoR/DoD Marking Tools and Dead Code Cleanup

**Status**: IMPLEMENTED

## User Story

- **Title:** Remove DoR/DoD Marking Tools and Dead Code Cleanup
- **As a:** Golazo Copilot developer
- **I want:** The `gcp_mark_dor` and `gcp_mark_dod` MCP tools removed, along with the orphaned `evidence.py` module (dead code per GCP-0025 Phase 3 design)
- **So that:** The MCP server is simplified to use automatic output validation via role files instead of manual checklist marking, with no orphaned modules left behind

## Out of Scope
- Modifying the output validation logic (already implemented in GCP-0025)
- Changing role file format (already updated in GCP-0026)
- Removing `checklists.py` (still actively used by `gcp_status.py`)
- Changing `output_validator.py` (replacement for `evidence.py`, already working)

## Assumptions
- **Assumption (explicit):** Existing work items with DoR/DoD state in `state.json` will continue to work — the state is preserved but the tools to update it are removed
- **Assumption (explicit):** `evidence.py` is dead code — no production source imports it; only `test_evidence.py` does
- **Assumption (explicit):** Interface type is MCP server (Python library), cross-platform, file-based persistence, technical users (developers)

## Acceptance Criteria
1. [ ] Mark tools removed: `gcp_mark_dor`, `gcp_mark_dod` tools gone from server; `gcp_mark.py` deleted; `tools/__init__.py` no longer exports them
2. [ ] Dead code removed: `evidence.py` and `test_evidence.py` deleted (per GCP-0025 Phase 3 design)
3. [ ] Tests for removed mark tools are deleted
4. [ ] Bootstrap instructions updated to remove `gcp_mark` examples
5. [ ] Output validation still works: `gcp_transition` validates required outputs from role files; `gcp_status` shows missing outputs AND the remediation action (what to create/fix)
6. [ ] All tests pass after cleanup (121+ tests)
7. [ ] Version bumped appropriately

## Non-Functional Requirements
- Breaking change: users upgrading from earlier versions will lose access to `gcp_mark_dor` and `gcp_mark_dod` tools
- No new dependencies introduced
- Test count should not decrease beyond the intentionally removed test files

## Telemetry / Metrics Expected
- N/A (local MCP server)

## Rollout / Rollback Notes
- Major version bump signals breaking change (removing 2 tools)
- No migration needed — `state.json` files remain valid, just the tools are gone
- Rollback: revert to previous version from git history
