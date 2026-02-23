# GCP-0052 Design Document: Subagent Handoff Protocol & Integration Testing

**Work Item:** GCP-0052  
**Author:** Program Manager  
**Status:** Draft

---

## Summary

GCP-0052 is the capstone work item for the 5-item subagent initiative (GCP-0048 through GCP-0052). It produces two deliverables: (1) a handoff protocol document defining how artifacts and context flow between sequential role subagents, and (2) an end-to-end integration test file that validates the full orchestrator → subagent → artifacts → next-subagent workflow.

## Problem Statement

The Golazo Copilot V2 MCP server uses a 10-role sequential workflow where each role produces artifacts consumed by subsequent roles. While individual components exist (self-contained role files with YAML front-matter from GCP-0048, `gcp_role_context` from GCP-0049, orchestration spine from GCP-0050), there is:

1. **No documented contract** specifying what the orchestrator must do at each transition boundary, what each subagent must produce, or how errors are recovered.
2. **No integration test** that walks the entire 10-role workflow end-to-end, verifying that `gcp_role_context` and `gcp_transition` work together correctly across all transitions.

Without these, future contributors lack a reference for the subagent architecture, and regressions at transition boundaries go undetected.

## Business Case

- **Why now:** GCP-0048/0049/0050 are complete — the subagent machinery exists but is unverified as an integrated system.
- **Impact:** Prevents silent breakage of the role pipeline. Documents the architecture for future contributors. Closes the subagent initiative with a verified, documented handoff contract.
- **KPIs:** All 10 role transitions validated in < 10 seconds. Handoff protocol ≤ 200 lines.

## Stakeholders

- **Golazo Copilot developers** — primary consumers of both the protocol document and the test suite.
- **Future contributors** — benefit from the documented handoff contract.

## Functional Requirements

### Deliverable 1: Handoff Protocol Document

**File:** `WorkItems/Golazo-Subagent-Handoff-Protocol.md`

Structure:

1. **Orchestrator Responsibilities** — What the orchestrator does at each transition boundary: calls `gcp_status` to get current state, invokes `gcp_role_context` to assemble the context bundle, delegates to the subagent, then calls `gcp_transition` when the subagent signals completion.

2. **Subagent Contract** — What each subagent receives (context bundle with role instructions, input artifacts, predecessor notes, state summary) and what it must produce (the `outputs:` listed in its YAML front-matter).

3. **Artifact Handoff Matrix** — A table mapping all 10 role transitions (from → to) with the specific artifact file patterns that bridge them. Derived directly from the `inputs:` and `outputs:` fields in the role default files:

   | From Role | To Role | Bridging Artifacts (outputs of From ∩ inputs of To) |
   |---|---|---|
   | project-owner-assistant | program-manager | `{id}-User-Story.md` |
   | program-manager | domain-expert | `{id}-User-Story.md`, `{id}-design-doc.md` |
   | domain-expert | quality-assurance | `{id}-User-Story.md`, `{id}-design-doc.md` |
   | quality-assurance | architect | `{id}-User-Story.md`, `{id}-design-doc.md`, `{id}-Review-Comments.md` |
   | architect | developer | `{id}-User-Story.md`, `{id}-design-doc.md`, `{id}-Review-Comments.md`, `{id}-Test-Cases.md` |
   | developer | refactor-expert | `{id}-developer.md` (role notes) |
   | refactor-expert | documenter | `{id}-User-Story.md`, `{id}-design-doc.md` |
   | documenter | builder | `{id}-User-Story.md` |
   | builder | retrospective | All 9 prior role notes |
   | retrospective | project-owner-assistant (closure) | `{id}-retrospective.md` |

4. **Error Recovery Strategy** — What happens when a subagent fails to produce required outputs: `gcp_transition` blocks with a list of missing files, the orchestrator retries the subagent or uses `gcp_consent` + `force` to skip outputs.

### Deliverable 2: Integration Test File

**File:** `golazo-copilot/tests/test_subagent_integration.py`

#### Test Structure

The test file uses `pytest` + `pytest-asyncio` with `tmp_path` fixtures. It calls `gcp_transition` and `gcp_role_context` directly (not mocking those tools) but simulates subagent work by creating files on disk.

**Test setup pattern:**
1. Create `tmp_path/WorkItems/<id>/` directory structure
2. Write `state.json` via `gcp_create_workitem`
3. Write role files under `tmp_path/.github/roles/` (loaded from package defaults or minimal stubs)
4. For each role transition: call `gcp_role_context`, assert it returns correct inputs, create the required output files, call `gcp_transition`, assert success

**Test cases:**

| ID | Test | Maps to AC |
|---|---|---|
| TC1 | `test_full_10_role_workflow` — Walks all 10 roles from POA through retrospective. At each step: calls `gcp_role_context` to verify inputs, creates mock outputs, calls `gcp_transition` to advance. | AC3 |
| TC2 | `test_negative_missing_output_blocks_transition` — Reaches a mid-workflow role, skips creating a required output, asserts `gcp_transition` returns `success=False` with the missing file path in the error. | AC4 |
| TC3 | `test_backward_transition_reentry` — Advances to developer, then transitions backward to architect, verifies `gcp_role_context` returns updated artifacts (not stale originals). | AC5 |
| TC4 | `test_no_regressions` — Covered by running the full existing test suite (AC6). Not a new test case — verified by CI. |

## Non-Functional Requirements

- Handoff protocol document ≤ 200 lines.
- Integration tests complete in < 10 seconds (no real I/O beyond temp directories, no network calls, no LLM invocations).
- Tests use `tmp_path` exclusively — no shared test state, no cleanup fixtures needed.

## Proposed Approach

### Phase 1: Handoff Protocol Document (Documenter deliverable during developer role)

1. Read all 10 role default files' YAML front-matter to extract `inputs:` and `outputs:`.
2. Build the handoff matrix by cross-referencing: for each transition N→N+1, the bridging artifacts are the set of files that appear in N's outputs or earlier outputs that N+1's inputs reference.
3. Document orchestrator responsibilities, subagent contract, the matrix, and error recovery.
4. Place at `WorkItems/Golazo-Subagent-Handoff-Protocol.md`.

### Phase 2: Integration Test File

1. Create `golazo-copilot/tests/test_subagent_integration.py`.
2. Implement helper functions:
   - `_make_role_files(project_root)` — Copies or creates role files with front-matter from package defaults.
   - `_create_mock_outputs(work_items_dir, wid, role)` — Creates the required output files for a given role (reads from front-matter `outputs:`).
3. Implement TC1: Full 10-role workflow walk.
4. Implement TC2: Negative case — skip output, assert blocked.
5. Implement TC3: Backward transition architect re-entry.
6. Verify AC6: Run full test suite to confirm no regressions.

## Key Technical Decisions

1. **Tests call `gcp_transition` and `gcp_role_context` directly** — We test the real tool functions, not mocks. This catches integration bugs at the boundary between tools. Mock files on disk simulate the subagent's work.

2. **Role files loaded from package defaults** — Tests copy role files from `golazo_copilot/roles/defaults/` into `tmp_path/.github/roles/`. This ensures tests use the actual front-matter, not stubs, making the handoff matrix test authoritative.

3. **`tmp_path` isolation** — Each test gets a fresh temp directory. No shared state, no cleanup fixtures. This enables parallel test execution without interference.

4. **Handoff matrix is derived, not hardcoded** — The protocol document's matrix is built by reading role front-matter directly, so it stays in sync with the actual role definitions.

5. **ROLE_SUFFIX_MAP used for note file creation** — Tests use `ROLE_SUFFIX_MAP` from `gcp_transition` to create correctly-named role note files (e.g., `refactor-expert` → `{id}-refactor.md`).

## Alternatives Considered

| Alternative | Reason Rejected |
|---|---|
| Mock `gcp_transition` and `gcp_role_context` in tests | Defeats the purpose — we want to test the real integration, not mocked stubs |
| Embed handoff matrix in code as a data structure | Protocol doc serves dual purpose: human reference + machine-verifiable. A code-only approach loses the documentation benefit |
| Test with real LLM calls | Too slow, non-deterministic, expensive. File-creation simulation is sufficient to validate the orchestration machinery |
| Single monolithic test for all 10 roles | Harder to diagnose failures. Separate test per concern (full walk, negative, backward) is clearer |

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Role file front-matter changes break tests | Medium | Medium | Tests read from package defaults. If front-matter changes, tests surface the drift immediately — that's the point |
| Large test file (> 300 lines) | Low | Low | Well-structured with helpers. Acceptable given it tests 10 role transitions |
| Backward transition semantics change | Low | Medium | TC3 explicitly tests the backward flow. Changes will be caught |
| `gcp_role_context` input resolution logic changes | Low | High | TC1 validates inputs at every step. Changes are caught early |

## Dependencies

- **GCP-0048** (complete): Self-contained role files with YAML front-matter providing `inputs:`, `outputs:`, `tools:`.
- **GCP-0049** (complete): `gcp_role_context` MCP tool that assembles context bundles from front-matter.
- **GCP-0050** (complete): Orchestration spine in `bootstrap-instructions.md`.

## Migration / Rollout / Rollback

- **Rollout:** Merge the protocol document and test file. No runtime impact — this is purely documentation + verification.
- **Rollback:** Delete `WorkItems/Golazo-Subagent-Handoff-Protocol.md` and `golazo-copilot/tests/test_subagent_integration.py`. No state changes to revert.

## Observability

- No runtime observability needed. Test results are the observability mechanism.
- Test failures surface via CI pipeline.

## Test Strategy

| Level | Scope | Method |
|---|---|---|
| Integration | Full 10-role workflow (TC1) | `pytest-asyncio`, `tmp_path`, real tool calls with mock file creation |
| Integration | Negative — missing output blocks (TC2) | Assert `gcp_transition` returns `success=False` with missing file info |
| Integration | Backward transition re-entry (TC3) | Advance to developer, go back to architect, verify context bundle |
| Regression | All existing 371+ tests (AC6) | Run full `pytest` suite — no changes to existing code |

**Success criteria:** All 3 new tests pass; all existing tests pass; protocol document exists and is ≤ 200 lines.
