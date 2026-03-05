# GCP-0052 Design Review Comments

**Work Item:** GCP-0052 — Subagent Handoff Protocol & Integration Testing  
**Reviewer:** Quality Assurance  
**Date:** 2026-02-22

---

## 1. Feasibility Assessment

**Verdict: Feasible with corrections.**

The design is structurally sound. Both deliverables (protocol document + integration tests) are achievable within the existing codebase. The test infrastructure (`pytest-asyncio`, `tmp_path`, real tool calls with mock file creation) is a proven pattern already used in `test_output_integration.py` and `test_gcp_role_context.py`. No new dependencies are required.

The `advance_to_role` helper in `test_gcp_transition.py` provides a ready-made pattern for walking role sequences. The existing `ROLE_SUFFIX_MAP` import and `create_role_notes` helper can be reused directly.

**Risk:** The design assumes `gcp_role_context` and `gcp_transition` can be called with `work_items_dir` and `project_root` overrides (for `tmp_path` isolation). This is confirmed by existing test patterns in `test_gcp_role_context.py` and `test_output_integration.py`.

---

## 2. Handoff Matrix Accuracy — Critical Correction Required

The domain expert's review (§2) identified **six discrepancies** in the design doc's handoff matrix. The design conflates "direct bridge" (predecessor outputs ∩ successor inputs) with "accumulated reach-back" (successor reads from earlier roles). This is the most significant finding.

### Specific Issues

| # | Transition | Design Doc Claim | Actual | Severity |
|---|---|---|---|---|
| 3 | DE → QA | User-Story + design-doc bridge | **Zero-bridge** — QA reaches back to POA & PM | High |
| 7 | Refactor → Documenter | User-Story + design-doc bridge | **Zero-bridge** — Documenter reaches back to POA & PM | High |
| 8 | Documenter → Builder | User-Story bridges | **Zero-bridge** — Builder reaches back to POA | High |
| 2 | PM → DE | User-Story + design-doc bridge | Only design-doc is direct; User-Story is reach-back to POA | Medium |
| 4 | QA → Architect | 3 artifacts bridge | Only Review-Comments is direct QA→Architect bridge | Medium |
| 10 | Retro → POA closure | retrospective.md bridges | **POA has `inputs: []`** — closure is unmodeled in front-matter | Medium |

**Recommendation:** The protocol document MUST present two views as the domain expert suggests: (a) direct bridge per transition, (b) full input set per role. The integration test assertions must use the actual front-matter `inputs:` / `outputs:`, not the design doc's idealized matrix.

---

## 3. Edge Cases Identified

### 3.1 Zero-Bridge Transitions (DE→QA, Refactor→Documenter, Documenter→Builder)

Three transitions have no direct artifact bridge from predecessor to successor. The successor's inputs come entirely from earlier roles. **Test impact:** TC1 must verify that `gcp_role_context` correctly sources inputs from non-adjacent predecessors. This is the most likely point of confusion for test authors assuming linear handoff.

### 3.2 Review-Comments Append Pattern

`Design/{id}-Review-Comments.md` is listed in both QA `outputs:` and Architect `inputs:` + `outputs:`. Architect appends to the QA-created file. **Test impact:** TC1 should verify that after Architect appends, the file contains content from both QA and Architect sections. An overwrite (instead of append) would silently lose QA review.

### 3.3 POA Closure Re-Entry

POA has `inputs: []` in its front-matter. When the workflow cycles back to POA after retrospective, there is no formal mechanism for `gcp_role_context` to inject retrospective findings. **Test impact:** The integration test should document what `gcp_role_context` actually returns for POA re-entry and flag any gap. This may warrant a follow-up work item.

### 3.4 `domain-expert` Missing from ROLE_SUFFIX_MAP

`domain-expert` is not explicitly listed in `ROLE_SUFFIX_MAP` (in `gcp_transition.py` lines 20–30). It falls through to the default `role` value via `.get(role, role)`, which yields `domain-expert`. This works correctly, but is implicit. **Test impact:** TC1 should use the correct suffix `domain-expert` (not a shortened form) for the domain-expert role notes file.

### 3.5 Capability-Impact.md — Non-Consumed Required Output

Architect outputs `Design/{id}-Capability-Impact.md` but no downstream role lists it as an input. `gcp_transition` still enforces it as a Required Output. **Test impact:** TC2 (negative case) could target this artifact for the missing-output scenario, but QA with its multiple outputs is a better target for testing granular error messages.

### 3.6 Retrospective Reads All 9 RDN Files

Retrospective's `inputs:` references all 9 prior role decision notes. **Test impact:** TC1 must create all 9 RDN files before reaching retrospective. Missing any one would cause `gcp_role_context` to mark it `[not yet created]`, which is valid behavior but should be explicitly verified.

---

## 4. Design Doc Gaps

### Gap 1: No Explicit Role File Setup Strategy for Tests

The design says "Tests copy role files from `golazo_copilot/roles/defaults/` into `tmp_path/.github/roles/`" but doesn't specify whether tests use the real package defaults or minimal stubs. The existing `test_output_integration.py` uses `create_role_file()` with inline content, while `test_gcp_role_context.py` uses `_write_role_file()` with explicit front-matter. **Recommendation:** Use the real package default files (copied into `tmp_path`) to keep the handoff matrix test authoritative. This is stated in the design's Key Technical Decision #2 but not reflected in the test structure section.

### Gap 2: TC3 Backward Transition — Incomplete Specification

The design says TC3 tests "developer → architect re-entry" but doesn't specify:
- What modified artifact should be checked after re-entry
- Whether `gcp_role_context` for architect on re-entry should show the developer's notes as a new input
- How the test verifies "updated artifacts, not originals"

**Recommendation:** TC3 should: (1) create initial Review-Comments during QA, (2) advance to developer, (3) transition backward to architect, (4) have architect update Review-Comments with new content, (5) verify the file contains both old and new content, (6) advance back to developer, (7) verify `gcp_role_context` for developer returns the updated Review-Comments.

### Gap 3: No Test for the `gcp_create_workitem` Setup Step

The test setup calls `gcp_create_workitem` to initialize `state.json`, but the design doesn't document what the initial state looks like or how role files get into `tmp_path`. This is an implementation detail but should be specified to avoid setup bugs.

### Gap 4: TC4 (No Regressions) Is Not a New Test

The design correctly notes that AC6 is covered by running the existing test suite, not a new test case. However, the protocol document should note that the CI pipeline is the enforcement mechanism for AC6.

---

## 5. Recommendations

1. **Use the domain expert's corrected matrix** (§2 of domain-expert notes) as the authoritative reference for both the protocol document and integration test assertions.

2. **Target QA role for TC2 (negative case)** — QA has three Required Outputs (`Review-Comments.md`, `Test-Cases.md`, `quality-assurance.md`). Omitting just `Test-Cases.md` and verifying the error message references the specific missing file tests granular gate enforcement.

3. **Add a TC for zero-bridge transitions** as a sub-case of TC1 — explicitly assert that `gcp_role_context` for QA returns User-Story and design-doc content even though DE (the predecessor) doesn't output either.

4. **Document POA closure as a known gap** in the protocol document rather than attempting to test something that doesn't exist in front-matter. Flag for a follow-up work item if closure context injection is needed.

5. **Reuse `advance_to_role` pattern** from `test_gcp_transition.py` — this helper creates notes and transitions through roles sequentially. Adapt it for the integration test to reduce boilerplate.

6. **Keep test file under 300 lines** — the design's non-functional requirement is < 10 seconds execution. Line count is secondary but the design notes 300 lines as a soft limit. Use helpers aggressively.

---

## 6. Approval

**Design approved with the corrections and recommendations above.** The domain expert's corrected handoff matrix must be used. The POA closure gap should be documented, not tested against non-existent behavior. All other aspects of the design are sound and implementable.

---

## Architect Notes

**Reviewer:** Architect  
**Date:** 2026-02-22

### 1. Architectural Review of the Integration Test Approach

The integration test strategy is architecturally sound. Key strengths:

- **Real tool calls, not mocks:** Testing `gcp_transition` and `gcp_role_context` directly with file-system simulation is the correct approach. Mocking these tools would hide the exact integration boundary bugs the tests are designed to catch — particularly the interplay between `output_validator.parse_required_outputs()` reading YAML front-matter and `gcp_transition` enforcing gate rules.
- **`tmp_path` isolation:** Each test gets a fresh directory tree with no shared state. This is the established pattern in the existing test suite (e.g., `test_output_integration.py`, `test_gcp_role_context.py`) and enables parallel execution via `pytest-xdist` without interference.
- **Real role files from package defaults:** Loading role files from `golazo_copilot/roles/defaults/` (not stubs) ensures the handoff matrix assertions stay authoritative. If a role file's `inputs:`/`outputs:` front-matter changes, these tests break immediately — that's the intended signal.

### 2. Contract Validation — Are Assertions Checking the Right Things?

**Positive assessment:** The test cases validate the correct contracts:

| Contract | Validated By | Assessment |
|---|---|---|
| `gcp_role_context` returns correct input artifacts | TC1 (every step), TC6 (zero-bridge) | Correct — verifies reach-back resolution, not just linear handoff |
| `gcp_transition` enforces Required Outputs | TC2 (negative case) | Correct — targets QA (3 outputs) for granular error validation |
| Backward transition preserves artifact freshness | TC3 (dev → architect → dev) | Correct — verifies no stale caching |
| `ROLE_SUFFIX_MAP` produces correct note filenames | TC7 | Correct — catches `refactor-expert` → `refactor` mapping |
| Protocol document structure + completeness | TC4 | Correct — static validation of the deliverable |

**Concerns addressed:**

- The domain expert's corrected matrix (distinguishing direct bridge vs. reach-back) MUST be used for TC1 assertions. The design doc's original matrix conflated the two. This is the single most important correction.
- TC1 Step 7 (refactor-expert) correctly asserts narrow scope: only `RDN/{id}-developer.md` appears in context, NOT design artifacts. This validates the intentional isolation of the refactoring phase.
- TC6 (zero-bridge transitions) is a critical addition. DE→QA, Refactor→Documenter, and Documenter→Builder have NO direct artifact bridge from predecessor. The assertions must prove `gcp_role_context` resolves inputs from non-adjacent earlier roles.

### 3. Test Fragility vs. Role File Changes

**Risk: Medium. Mitigation: By design.**

The tests read front-matter from the actual role default files. If a role's `inputs:` or `outputs:` change, tests that assert on the artifact flow will fail. This is **intentional** — the tests serve as a regression guard on the artifact contract. However:

- **Recommendation:** Tests should NOT hardcode artifact file paths as string literals scattered through test functions. Instead, use a single `EXPECTED_OUTPUTS` dict (derived from front-matter at test-module level) so that when a role file changes, the test update is centralized.
- **Recommendation:** The `_create_mock_outputs` helper should read the role file's `outputs:` front-matter dynamically (via `parse_required_outputs`) rather than using a hardcoded list. This keeps the helper self-maintaining.
- **Accepted fragility:** If the `ROLE_SUFFIX_MAP` changes (e.g., `refactor-expert` is renamed), TC7 will break. This is acceptable — the suffix map is a critical contract that downstream tools depend on.

### 4. Security Review

**N/A — confirmed.** This work item produces:
1. A documentation file (`WorkItems/Golazo-Subagent-Handoff-Protocol.md`) — no executable code, no secrets, no user-facing endpoints.
2. A test file (`golazo-copilot/tests/test_subagent_integration.py`) — runs in CI, operates on `tmp_path`, no network calls, no credential handling.

No security concerns apply. No new attack surface, no data exposure, no auth boundary changes.

### 5. Additional Architectural Observations

1. **Review-Comments append pattern:** Architect lists `Review-Comments.md` in both `inputs:` and `outputs:`. The integration test MUST verify append-not-overwrite semantics — after Architect executes, the file should contain both QA and Architect sections. An overwrite would silently lose QA review content.

2. **Capability-Impact.md is non-consumed:** Architect produces it but no downstream role reads it. `gcp_transition` still enforces it as a Required Output. The negative test (TC2) should NOT use this artifact as the "missing" item — use QA's `Test-Cases.md` instead, as QA has more outputs for granular testing.

3. **POA closure gap:** POA has `inputs: []`. The protocol document should document this as a known limitation — closure context injection is an orchestrator-level concern not modeled in front-matter. Do NOT attempt to test behavior that doesn't exist.

4. **Test execution time:** The < 10 second NFR is achievable. All operations are local filesystem I/O on `tmp_path`. No network calls, no LLM invocations. The existing `test_output_integration.py` runs a similar pattern in < 2 seconds.
