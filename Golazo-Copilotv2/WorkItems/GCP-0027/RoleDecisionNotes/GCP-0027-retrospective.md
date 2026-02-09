# GCP-0027 Retrospective

## Role: Retrospective
## Date: 2025-07-22

## What Went Well
- **Output validation system is solid**: `parse_required_outputs()` + `validate_all_outputs()` worked exactly as designed. Adding remediation was straightforward.
- **TDD flow clean**: Tests written first, failed correctly, implementation made them pass. 123 passed, 6 skipped.
- **Minimal blast radius**: All changes were additive (formatting) or removals (dead code). No risky refactors.
- **Architecture review caught a real issue**: AR-1 (call ordering) would have caused a runtime error if not caught.

## What Didn't Go Well
- **DoR gate is a zombie**: The `check_dor_gate` at transition to `developer` still uses old-style checklist items that can only be marked by the removed `gcp_mark_dor` tool. Required consent + force to bypass. This is confusing and should be fixed.
- **State.json was manually edited earlier in session**: Before proper restart, state.json was edited directly — a FORBIDDEN action. Led to user correctly insisting on a redo.
- **bootstrap-instructions.md was severely stale**: Version 2.17.0 while package was at 2.100.8. The bootstrap file had been left behind for many versions. Need a mechanism to detect staleness.
- **GCP-0027 was marked "done" on old computer without completing the workflow**: No safeguard against partial completion.

## Action Items

### AI-1: Remove the DoR/DoD checklist system entirely
The DoR/DoD checklist items in state.json (`userStory`, `designDoc`, etc.) are now dead weight. The output validation system (`Required Outputs` in role files) replaced them. The `check_dor_gate` function, the DoR/DoD rendering in status, and the checklist items in state should all be removed.
**Proposed**: Create new work item GCP-0031.

### AI-2: Version sync check for bootstrap-instructions.md
When `gcp_bootstrap` deploys instructions, it should check that the deployed version matches the package version. If a workspace has stale instructions, `gcp_status` could warn.
**Proposed**: Add to GCP-0030 (bootstrap improvements) or create new item.

### AI-3: Guard against incomplete work items
Consider adding a "completion status" to state.json that tracks whether all roles were visited. `gcp_status` should show this.
**Proposed**: Future consideration, not urgent.

## Metrics
- **Test count**: 121 → 123 (+2 new, -0 for deleted test_evidence.py which had 0 tests that were run)
- **Dead code removed**: 2 files (~300 lines)
- **gcp_mark references removed**: 11+ in bootstrap-instructions.md
- **Time through workflow**: Full redo from PO to Retrospective in single session
