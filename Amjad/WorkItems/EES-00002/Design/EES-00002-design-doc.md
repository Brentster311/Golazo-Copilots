# EES-00002 — Design Doc: GAP Rule Detection and Refinement

## Summary

Extend the expert system's rule generation pipeline to detect when an incident establishes known starting conditions and a known root cause but lacks intermediate diagnostic steps. When this gap is detected, the system creates explicit **GAP rules** that bridge the known endpoints. As subsequent incidents provide the missing intermediate steps, the system refines or resolves existing GAP rules.

## Problem Statement

EES-00001 generates CONFIRMED rules only when the LLM proposes complete diagnostic chains. Incidents that show correlation between symptoms and root causes — but where the intermediate diagnostic logic is unclear — produce no rules at all. This means incomplete knowledge is silently lost. Over time, these missing chains represent the most valuable diagnostic gaps to close.

## Business Case

- **Why now:** GAP detection is the first incremental enhancement after the core learning loop. Without it, the knowledge base only captures "fully understood" diagnostics, ignoring the most common real-world scenario: "we know what happened but not exactly why."
- **Impact:** Captures diagnostic knowledge that would otherwise be lost. Each GAP rule is a prioritized investigation target.
- **KPIs:**
  - Number of GAP rules created per incident
  - GAP refinement rate (GAPs narrowed or resolved per incident)
  - Total open GAP count (lower = more complete knowledge base)

## Stakeholders

- **Technical user** — sees GAP rules during processing, understands what knowledge is missing
- **Knowledge base** — accumulates explicit "unknowns" that guide future investigation

## Functional Requirements

### FR-1: GAP Detection
When `process_incident` completes fact confirmation and rule generation:
1. Check if the incident has a confirmed root cause
2. Check if any confirmed facts exist that are NOT connected to the root cause through existing or newly-confirmed rules
3. If disconnected facts exist, create a GAP rule bridging them

### FR-2: GAP Rule Model
A GAP rule extends the existing `Rule` model with:
- `status: "GAP"` (vs `"CONFIRMED"`)
- `requires`: list of input facts (the known starting conditions)
- `produces`: list of output facts (the known ending conditions)
- `note`: human-readable description of what's unknown
- Standard `sources`, `rule_id`, and `because` fields

### FR-3: GAP Rule Persistence
GAP rules are persisted in `rules/` alongside CONFIRMED rules, using the same YAML format with additional `requires`/`produces`/`note` fields. They use the same `R-NNN` ID scheme.

### FR-4: GAP Refinement
When a new incident produces rules that overlap with an existing GAP's `requires`/`produces` boundaries:
1. Detect the overlap (new rule's conditions match GAP's `requires` facts, or new rule's `then` matches GAP's `produces` facts)
2. If the new rules fully connect `requires` → `produces`: resolve the GAP (update status to `RESOLVED`)
3. If partially filled: narrow the GAP (update `requires`/`produces` to reflect remaining unknown, add new incident to `sources`)
4. Report the refinement to the user

### FR-5: GAP Reporting
During incident processing, report:
- New GAP rules created
- Existing GAP rules narrowed
- Existing GAP rules resolved

## Non-Functional Requirements

- GAP rules must clearly distinguish known (requires/produces) from unknown (the gap)
- No data loss during GAP decomposition — all source incident IDs are preserved
- GAP rules are human-readable in YAML output
- Backward compatible — existing CONFIRMED rules are unaffected

## Proposed Approach

### Phase 1: Model Changes
- Extend `Rule.status` type to accept `"CONFIRMED" | "GAP" | "RESOLVED"`
- Add optional fields to `Rule`: `requires`, `produces`, `note`
- Update `Rule.to_dict()` / `Rule.from_dict()` for the new fields

### Phase 2: GAP Detection Logic
- New module `gap_detector.py` with class `GapDetector`
- After confirmed rules are generated, `GapDetector.detect_gaps()` analyzes:
  - Confirmed facts → which facts are "consumed" by confirmed rule conditions
  - Root cause → which facts lead to it through confirmed rules
  - Orphaned facts → facts that exist but don't connect to the root cause
- Creates GAP rules bridging orphaned facts to the root cause

### Phase 3: GAP Refinement Logic
- `GapDetector.check_refinements()` runs against existing GAP rules
- Compares new confirmed rules' condition/then boundaries against GAP requires/produces
- Returns list of refinement actions (narrow/resolve)

### Phase 4: Integration into main.py
- Insert GAP detection between rule confirmation (Step 6) and ontology update (Step 7)
- Insert GAP refinement check after GAP detection
- Add GAP summary to the final report

### Phase 5: User Confirmation of GAPs
- Present detected GAPs to the user for confirmation (c/e/r), similar to rules
- User can edit the `note` field to describe what they think is missing

## Alternatives Considered

| Alternative | Why Rejected |
|-------------|-------------|
| LLM detects GAPs directly | Unreliable — LLM doesn't have knowledge-base context. Better to use deterministic graph analysis on confirmed facts. |
| Separate GAP file format | Adds complexity. GAP rules in `rules/` with `status: GAP` keeps them integrated. |
| Automatic GAP resolution without user confirmation | Risky — user should confirm GAP refinements to avoid silent knowledge corruption. |

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| GAP detection generates too many false positives | Medium | Low | User confirmation step filters noise; conservative detection (require root cause) |
| GAP refinement incorrectly narrows a GAP | Low | Medium | User confirmation of refinements; source provenance preserved for audit |
| Model extension breaks existing rule loading | Low | High | `from_dict()` uses `.get()` with defaults for new optional fields |

## Open Questions

| # | Question | Proposed Resolution |
|---|----------|-------------------|
| OQ-1 | How "deep" should chain analysis go? Should it trace multi-hop rule chains? | Start with single-hop: facts → rules → root cause. Multi-hop is a future enhancement. |
| OQ-2 | Should GAP rules be included when the LLM receives ontology context? | No — GAPs represent unknown logic, sending them to the LLM could confuse extraction. |
| OQ-3 | Should resolved GAPs be deleted or kept with status RESOLVED? | Keep with RESOLVED status for audit trail. |

## Dependencies

- **EES-00001** — Core learning loop must be complete (✅ done)
- No new external dependencies beyond existing stack

## Migration / Rollout / Rollback

- **Migration:** None needed. New fields in Rule YAML are additive; existing rules without `requires`/`produces`/`note` load fine via `from_dict()` defaults.
- **Rollout:** Feature is active as part of normal `ees process` workflow. No feature flags needed.
- **Rollback:** `git revert` — existing CONFIRMED rules are unaffected. GAP rules are simply removed.

## Observability Plan

- CLI output reports GAPs created/narrowed/resolved per incident
- Summary line: "GAPs: X created, Y narrowed, Z resolved"

## Test Strategy Summary

| Area | Approach |
|------|----------|
| GAP detection logic | Unit tests with mock facts/rules — verify orphaned facts produce GAP rules |
| GAP refinement logic | Unit tests with existing GAP rules + new incoming rules |
| Model serialization | Roundtrip tests for Rule with GAP fields |
| Integration | Mocked `process_incident` tests with GAP scenarios |
| Edge cases | No root cause → no GAPs; all facts connected → no GAPs; empty confirmed facts |
