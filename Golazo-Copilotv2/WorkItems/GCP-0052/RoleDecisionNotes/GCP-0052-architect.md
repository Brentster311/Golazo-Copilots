# GCP-0052 Architect — Decision Notes

**Work Item:** GCP-0052 — Subagent Handoff Protocol & Integration Testing  
**Role:** Architect  
**Date:** 2026-02-22

---

## Architectural Alignment Assessment

GCP-0052's deliverables align correctly with the Golazo Copilot architecture:

1. **Handoff protocol document** codifies the existing artifact flow that is already implicit in role file YAML front-matter (`inputs:`/`outputs:`). It does not introduce new architecture — it documents the existing contract. This is the right approach: the architecture already exists in code; what was missing was a human-readable reference.

2. **Integration test file** validates the real tool integration boundary (`gcp_role_context` + `gcp_transition`) across all 10 role transitions. This closes the gap identified in the subagent initiative (GCP-0048–0052): individual components were tested, but the end-to-end flow was not. The test file is a pure consumer of existing contracts — it doesn't introduce new abstractions or coupling.

3. **No production code changes** — correct. The architecture is already built (GCP-0048/0049/0050). This work item verifies and documents it.

---

## Test Structure Recommendations

### 1. Use Dynamic Output Discovery, Not Hardcoded Paths

Tests should derive expected outputs from role file front-matter using `parse_required_outputs()` rather than hardcoding file paths. This keeps tests self-maintaining when role definitions evolve.

```python
# Preferred: dynamic
from golazo_copilot.core.output_validator import parse_required_outputs
role_content = load_role_instructions(role, project_root)
specs = parse_required_outputs(role_content, work_item_id)

# Avoid: hardcoded
EXPECTED = {"quality-assurance": ["Review-Comments.md", "Test-Cases.md", ...]}
```

### 2. Centralize Role Sequence and Suffix Mapping

Import `ROLE_ORDER` from `transitions.py` and `ROLE_SUFFIX_MAP` from `gcp_transition.py` rather than redefining them in the test file. Single source of truth for the role sequence.

### 3. Reuse `advance_to_role` Pattern

The existing `test_gcp_transition.py` has an `advance_to_role` helper. The integration test should adapt this pattern to reduce boilerplate. The helper creates required outputs and calls `gcp_transition` for each intermediate role.

### 4. Separate Concerns Across Test Functions

- TC1 (full walk): Happy path, linear progression, all outputs created.
- TC2 (negative): Gate enforcement — omit one output, verify blocked.
- TC3 (backward): Non-linear flow — verify artifact freshness after re-entry.
- TC6 (zero-bridge): Reach-back resolution — verify non-adjacent input sourcing.
- TC7 (suffix map): Data-driven assertion on a critical mapping.

Each test should be independently runnable (no ordering dependency).

### 5. Keep Test File Under 300 Lines

Use helper functions aggressively:
- `_setup_workspace(tmp_path)` — copies role defaults, initializes work item
- `_create_outputs_for_role(role, wid, work_items_dir)` — creates all Required Outputs for a role using front-matter
- `_advance_through(roles, wid, work_items_dir, project_root)` — walks a sequence of roles

---

## Risks Identified

| Risk | Severity | Mitigation |
|---|---|---|
| Handoff matrix in protocol doc drifts from actual front-matter | High | TC1 assertions are derived from real front-matter, not the protocol doc. Drift is caught at test time. |
| Role file `inputs:`/`outputs:` changes break integration tests | Medium | Intended behavior — tests are the regression guard. Use dynamic output discovery to minimize maintenance. |
| `gcp_role_context` changes input resolution logic | Medium | TC1 and TC6 validate input resolution at every step. Changes surface immediately. |
| POA closure re-entry is not testable via front-matter | Low | Document as known gap in protocol doc. Don't test non-existent behavior. |
| Review-Comments overwrite instead of append | Medium | TC1 Step 5 must assert both QA and Architect content exist after Architect executes. |
| Test execution exceeds 10-second NFR | Low | All I/O is `tmp_path` local filesystem. Existing similar tests run in < 2 seconds. |

---

## Decisions Made

1. **Approved the domain expert's corrected handoff matrix** as the authoritative reference for both the protocol document and integration test assertions. The design doc's original matrix conflated direct bridges with accumulated reach-back.

2. **Confirmed no capability registry update needed.** Tests are consumers of capabilities, not capabilities themselves. No production code is changed.

3. **Recommended dynamic output discovery** over hardcoded paths in tests — use `parse_required_outputs()` to read front-matter and derive expected files.

4. **Confirmed QA role as the target for TC2** (negative case) — QA has 3 Required Outputs, making it ideal for testing granular gate error messages.

5. **Endorsed the POA closure gap documentation** rather than attempting to test behavior that doesn't exist in front-matter. Follow-up work item may be warranted if closure context injection is needed.

6. **No security concerns.** Both deliverables are non-executable documentation and test code with no network calls, credential handling, or user-facing surface.

---

## Conclusion

The design is architecturally sound. No structural changes needed. The integration tests correctly target the tool integration boundary and the handoff matrix domain expert corrections must be incorporated. Ready to proceed to developer role.
