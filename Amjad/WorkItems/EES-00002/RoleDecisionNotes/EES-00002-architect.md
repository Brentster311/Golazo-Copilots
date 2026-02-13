# EES-00002 — Architect Decision Notes

**Role:** architect  
**Work Item:** EES-00002 — GAP Rule Detection & Refinement  
**Date:** 2025-02-01

## Review Scope

Reviewed design doc, QA review comments (3 major + 3 minor findings), user story, expert-system-decisions.md, and all production source files (models.py, yaml_store.py, rule_generator.py, main.py).

## Findings Addressed

### QA Major Findings — All Resolved

| Finding | Resolution |
|---------|-----------|
| MJ-1: Orphaned fact algorithm | Single-hop, match_key-based. Fact is connected if ANY CONFIRMED rule uses it in conditions AND that rule's then-clause targets the root cause. |
| MJ-2: No root cause behavior | Skip GAP detection entirely. No root cause = no endpoint to bridge toward. |
| MJ-3: Refinement matching | Subset matching via match_key(). Compute remaining = gap_requires - new_rule_conditions. Empty remaining + bridge to produces = RESOLVED. Smaller remaining = NARROWED. |

### QA Minor Findings — All Resolved

| Finding | Resolution |
|---------|-----------|
| MN-1: requires/produces on Rule | Accepted. Optional fields, conditionally serialized. |
| MN-2: RESOLVED status | Accepted as GAP lifecycle detail. |
| MN-3: filter_rules GAP exclusion | Yes — is_duplicate() skips GAP-status rules. A confirmed rule matching a GAP is a refinement, not a duplicate. |

## Architectural Decisions (7)

### A-1: Rule Model Extension
- `Rule.status` → `Literal["CONFIRMED", "GAP", "RESOLVED"]`
- New fields: `requires: list[Fact] = []`, `produces: list[Fact] = []`, `note: str = ""`
- Conditional serialization: only emit GAP fields when non-default
- Backward compatible: `from_dict()` uses `.get()` with defaults

### A-2: Serialization Contract
requires/produces serialized as condition-item dicts (no status field), matching RuleConditions.items format for consistency.

### A-3: GapDetector Module
- New `src/ees/gap_detector.py` with `GapDetector` class
- Pure logic, no I/O — YamlStore interaction stays in main.py
- `detect_gaps()` and `check_refinements()` methods

### A-4: GapRefinement Result Type
New `GapRefinement` dataclass in models.py: `gap_rule_id`, `action` (narrowed/resolved), `updated_rule`.

### A-5: R-007 Decomposition Deferred
The 3-rule decomposition pattern (a/b/c with synthetic intermediate facts) from expert-system-decisions.md is deferred. EES-00002 uses single-GAP-rule approach.

### A-6: One GAP Per Incident
Single-hop detection produces at most one GAP rule per incident (all orphaned facts grouped).

### A-7: Integration Point
Inserts between rule confirmation (step 6) and ontology update (step 7) in process_incident.

## Security & Privacy
- No new external dependencies
- No new secrets or credentials
- GAP rules are stored locally alongside existing rules
- No LLM involvement in GAP detection (deterministic)

## Blast Radius
- **Rule model change**: Affects Rule.to_dict/from_dict, is_duplicate, yaml_store load/save. Low risk — additive optional fields with defaults.
- **filter_rules change**: 1-line guard clause. Low risk — only affects dedup behavior for GAP-status rules (which don't exist yet).
- **main.py integration**: Inserting new workflow step. Moderate risk — must not disrupt existing steps 1-8.
- **Rollback**: `git revert` — additive YAML fields are harmless. GAP rule files can be deleted.

## Implicit Assumptions Surfaced
1. `rule.then.noun.lower() == "rootcause"` is the convention for root-cause rules — confirmed by reviewing existing main.py _confirm_root_cause and FactExtractor behavior
2. `Fact.match_key()` normalization (noun/property lowered, case-sensitive instance/operator/value) is correct for orphaned-fact matching — confirmed, consistent with rule_generator.py usage
3. ruamel.yaml handles `requires: []` (empty list) without issues on load — confirmed, safe behavior

## Recommendation
Design is **approved** with the 7 architectural decisions documented in Review-Comments.md. Ready for developer role.
