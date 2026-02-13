# EES-00002 — Developer Decision Notes

**Role:** developer  
**Work Item:** EES-00002 — GAP Rule Detection & Refinement  
**Date:** 2025-02-01

## TDD Approach

All code written test-first following red→green cycle:

1. **Model tests (10 new)** → Extended Rule with GAP fields, added GapRefinement
2. **GapDetector tests (18 new)** → detect_gaps + check_refinements 
3. **RuleGenerator tests (2 new)** → is_duplicate skips GAP rules
4. **Main integration tests (7 new)** → _confirm_gaps + process_incident GAP workflow

## Production Changes

### `src/ees/models.py`
- `Rule.status` → `Literal["CONFIRMED", "GAP", "RESOLVED"]`
- Added: `requires: list[Fact]`, `produces: list[Fact]`, `note: str`
- `to_dict()`: conditionally emits GAP fields (omits when default)
- `from_dict()`: `.get()` with defaults for backward compat
- Added `GapRefinement` dataclass

### `src/ees/gap_detector.py` (NEW)
- `GapDetector.__init__(existing_rules)`
- `detect_gaps(confirmed_facts, new_rules, root_cause, incident_id) → list[Rule]`
- `check_refinements(new_rules, incident_id) → list[GapRefinement]`
- Pure logic, no I/O

### `src/ees/rule_generator.py`
- `is_duplicate()`: added `if existing.status == "GAP": continue`

### `src/ees/main.py`
- Added `_confirm_gaps()` for interactive GAP confirmation (c/e[note]/r)
- Inserted GAP detection between step 6 (rules) and step 7 (ontology)
- GAP summary: "GAPs: X created, Y narrowed, Z resolved"

## Test Results

- **140 tests passed**, 0 failed
- **98% coverage** overall
- **96% coverage** on gap_detector.py (2 uncovered lines: edge cases in complex branches)
- All 5 acceptance criteria verified:
  - AC-1: GAP created for orphaned facts ✅
  - AC-2: GAP persisted with status: GAP and sources ✅
  - AC-3: GAP refinement (narrow/resolve) ✅
  - AC-4: GAP reporting in summary ✅
  - AC-5: GAP distinguishable from CONFIRMED in YAML ✅

## Design Deviations

None. Implementation exactly matches design doc + architect decisions.
