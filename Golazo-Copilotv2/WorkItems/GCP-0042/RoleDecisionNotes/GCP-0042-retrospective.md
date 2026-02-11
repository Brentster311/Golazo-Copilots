# Retrospective — GCP-0042

## What went well
- Self-contained `_get_registry_hint()` function is testable in isolation with `tmp_path` — no complex mocking needed
- Architect recommendation to avoid coupling to `gcp_capabilities.py` kept the change small and independent
- 7 test cases cover all edge cases (absent, valid, malformed, missing key, empty list, integration)

## What didn't go well

### SFI-026 Process Gap: capabilities.yaml not consulted

**Symptom:** During the SFI-026 workflow, `capabilities.yaml` was neither read (impact analysis) nor written (contract updates). It was only updated as an afterthought when the user asked.

**Cause:** Role instructions say "if capabilities.yaml exists, run `gcp_capabilities(action='impact')`" but this is framed as optional/advisory (under `### Capability Registry (if capabilities.yaml exists)`). No gate enforces it, so it was skipped at every role — PM design, Architect review, Developer implementation, and Builder commit.

**Impact:**
- Design didn't identify downstream dependents (e.g. `reporter-build`, `reporter-tests`) that would be affected by file changes
- New public contracts weren't registered until post-completion
- New test files weren't added to capability `key_files` until post-completion

**Root cause:** The current gate system only validates file/dir/git-branch/git-log existence. Capability consultation is purely advisory text in role instructions with no enforcement mechanism.

## Action items

### AI-1: Architect — Gate capability impact analysis (role file change)

**Change:** Add a required output `file: WorkItems/{id}/Design/{id}-Capability-Impact.md` to the Architect role. Change the "Capability Registry" section from optional advisory to a required responsibility.

**Concrete diff to `.github/roles/architect.md`:**
- Remove `(if capabilities.yaml exists)` qualifier from section heading
- Add explicit instruction: when `capabilities.yaml` exists, create `{id}-Capability-Impact.md` documenting the impact analysis results (directly affected, transitively affected, contract implications). When no `capabilities.yaml` exists, create the file with "N/A — no capabilities.yaml in project."
- Add `- file: WorkItems/{id}/Design/{id}-Capability-Impact.md` to Required Outputs

**Why this works:** The gate system already validates `file:` entries. The Architect cannot transition without this file existing.

### AI-2: Builder — Gate capability registry validation (role file change)

**Change:** Add capability registry responsibilities to the Builder role. After build verification and before final commit:
1. Run `gcp_capabilities(action="validate")` to confirm all `key_files` still exist
2. If new public functions/contracts were introduced by the work item, update `capabilities.yaml` (add new contracts, key_files, dependencies)
3. Document validation results in builder notes

**Concrete diff to `.github/roles/builder.md`:**
- Add a `### Capability Registry Validation` section to Responsibilities
- The builder notes (already gated) must include a "Capability Registry" section documenting whether capabilities.yaml was validated and whether updates were needed

**Why this works:** Builder notes are already a required gate. The role instructions mandate what must be in those notes. This is a softer gate than the Architect's file gate, but appropriate for the Builder's scope.

### AI-3: Follow-up work item — Conditional gate support (optional, code change)

**Proposed:** Add a new output spec type `file-if: <condition-path> -> <required-path>` that only enforces the required path if the condition path exists. Example: `file-if: capabilities.yaml -> WorkItems/{id}/Design/{id}-Capability-Impact.md`. This would let us conditionally enforce gates for projects that have capabilities.yaml without burdening projects that don't.

**Priority:** Low — AI-1's approach of "create with N/A content" is a viable workaround.

## Metrics
- Cycle: ~8 min
- Test delta: +7 (180 → 187)
- Zero defects

## Session Summary (all backlog items)
| Work Item | Title | Tests Added | Commit |
|-----------|-------|-------------|--------|
| GCP-0037 | Per-File Stale Version Reporting | 10 | `d6ac2d8` |
| GCP-0039 | Role Instructions — Reference Capability Registry | 10 | `228b5e5` |
| GCP-0040 | Bootstrap — Scaffold capabilities.yaml Template | 7 | `f12eead` |
| GCP-0041 | Spine — Mention Capability Registry | 3 | `32ff20c` |
| GCP-0042 | gcp_status — Surface Registry Hints | 7 | `ad65723` |
| **Total** | | **37 new tests** (150 → 187) | **5 commits** |
