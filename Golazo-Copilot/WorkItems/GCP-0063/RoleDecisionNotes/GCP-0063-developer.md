# Role Decision Notes — Developer

## Work Item
- ID: GCP-0063
- Role: developer
- Date: 2026-03-05

## Assumptions Applied
1. Approved implementation scope is limited to items 1, 2, and 3 from the design doc.
2. The canonical policy wording should be identical across orchestrator and handoff documentation to prevent drift.
3. Existing retrospective-specific behavior remains out of scope for behavioral refactoring; this change focuses on explicit default policy wording.

## TDD Execution Record
### Red phase (tests added first)
- Added: `golazo-copilot/tests/test_gcp0063_role_execution_policy.py`
- Initial run:
  - Command: `python -m pytest golazo-copilot/tests/test_gcp0063_role_execution_policy.py -q`
  - Result: `4 failed, 1 passed`
  - Failing areas matched expected gaps:
    - `DEFAULT_ROLES` missing `domain-expert.md`
    - `_DEPLOYED_TO_SOURCE` missing `domain-expert.md` mapping
    - Orchestrator/handoff docs missing required aligned policy text

### Green phase (implementation)
- Updated code/doc files to satisfy AC1–AC5.
- Re-run targeted tests:
  - Command: `python -m pytest golazo-copilot/tests/test_gcp0063_role_execution_policy.py -q`
  - Result: `5 passed`

### Regression slice
- Command: `python -m pytest golazo-copilot/tests/test_gcp_bootstrap.py golazo-copilot/tests/test_gcp_status.py -q`
- Result: `58 passed`

## Implementation Decisions
1. Added `domain-expert.md` exactly once in bootstrap default role copy list.
2. Added deployed-to-source version mapping for `domain-expert.md` in status tool.
3. Introduced explicit role execution matrix language in orchestrator docs:
   - Design roles run inline and may ask user questions.
   - Non-design roles run as subagents by default.
   - No-question rule scoped to subagent execution.
4. Adopted a single canonical fallback sentence and applied it verbatim to both orchestrator and handoff docs.
5. Mirrored orchestrator policy changes in source bootstrap template to keep generated instructions aligned with deployed instructions.

## Files Changed
- `golazo-copilot/tests/test_gcp0063_role_execution_policy.py`
- `golazo-copilot/src/golazo_copilot/tools/golazo_bootstrap.py`
- `golazo-copilot/src/golazo_copilot/tools/golazo_status.py`
- `.github/agents/Golazo-Copilot.md`
- `golazo-copilot/src/golazo_copilot/bootstrap-instructions.md`
- `WorkItems/Golazo-Subagent-Handoff-Protocol.md`

## Capability Registry Check
- Ran `golazo_capabilities(action="impact", files=[...])` for all planned changed files.
- Result: `0 capabilities affected`.

## Scope Compliance
- No dependency additions.
- No workflow gate/state model rewrites.
- No out-of-scope DoR/DoD model changes.
- No rejected-item (6/7) implementation.
