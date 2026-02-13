# Refactor Decision Notes — EES-00001

## Summary

Applied 4 refactorings to improve code quality, reduce duplication, and remove architectural violations. All tests remain green (69 passed: 66 original + 3 new tests for `Fact.match_key()`).

---

## Refactorings Applied

### RF-1: Extract Custom Exceptions from Library Classes (High Priority)

**Problem:** `incident_loader.py` and `fact_extractor.py` called `sys.exit(1)` directly — a CLI concern leaking into library code. This makes these classes untestable in non-CLI contexts and couples them to a specific error-handling strategy.

**Change:**
- Created `src/ees/exceptions.py` with `IncidentLoadError`, `LLMError`, and `ConfigError`
- `incident_loader.py` — replaced 4 `sys.exit(1)` calls with `raise IncidentLoadError(...)`
- `fact_extractor.py` — replaced 3 `sys.exit(1)` calls with `raise ConfigError(...)` or `raise LLMError(...)`
- `main.py` — added try/except at CLI boundary to catch all three exceptions and call `sys.exit(1)` with error message

**Files Changed:** `exceptions.py` (new), `incident_loader.py`, `fact_extractor.py`, `main.py`, `test_incident_loader.py`, `test_fact_extractor.py`

**Test Impact:** Updated tests to expect `IncidentLoadError`/`LLMError` instead of `SystemExit`. All 66 tests still pass.

---

### RF-2: Eliminate Duplicated Fact-from-Dict Construction (High Priority)

**Problem:** `RuleConditions.from_dict()` and `FactExtractor._parse_response()` both manually constructed `Fact(noun=d["noun"], ...)` instead of using the existing `Fact.from_dict()` class method.

**Change:**
- `models.py` — `RuleConditions.from_dict()` now uses `Fact.from_dict(it)` instead of inline construction
- `fact_extractor.py` — `_parse_response()` now uses `Fact.from_dict({**f, "instance": f.get("instance", "*")})` to handle the optional `instance` key

**Files Changed:** `models.py`, `fact_extractor.py`

**Test Impact:** No test changes needed. All 66 tests pass.

---

### RF-3: Remove Deferred Imports in main.py (Medium Priority)

**Problem:** `main.py` had two `from ees.models import Incident` statements deferred inside `process_incident()` instead of at the top-level. No circular dependency existed.

**Change:** Moved `Incident` to the top-level import and removed both inline imports.

**Files Changed:** `main.py`

**Test Impact:** None. All tests pass.

---

### RF-4: Add Fact.match_key() Method (Medium Priority)

**Problem:** `rule_generator.py` inline-constructed a 5-tuple `(f.noun.lower(), f.instance, f.property.lower(), f.operator, f.value)` for case-insensitive matching. This knowledge about how to normalize a Fact for comparison was scattered outside the `Fact` class.

**Change:**
- `models.py` — added `Fact.match_key() -> tuple[str, str, str, str, str]` that returns the normalized 5-tuple
- `rule_generator.py` — replaced inline tuple construction with `f.match_key()` / `item.match_key()`
- `test_models.py` — added 3 new tests for `match_key()` (case normalization, instance preservation, cross-case equality)

**Files Changed:** `models.py`, `rule_generator.py`, `test_models.py`

**Test Impact:** 3 new tests added. Total: 69 passed.

---

## Findings Deferred (No Action Taken)

| Finding | Reason Deferred |
|---------|----------------|
| `process_incident()` is ~100 lines | Extract helpers would change module API; better addressed in future work item |
| `is_duplicate_of()` uses dict comparison | Functionally correct and readable; premature to optimize |
| No `__hash__` on Fact | Would require `frozen=True` which conflicts with mutable `status` field |
| Scattered case normalization in OntologyManager | Working correctly; centralization would be over-engineering at this scope |

---

## Test Results

| Metric | Before | After |
|--------|--------|-------|
| Total Tests | 66 | 69 |
| Passing | 66 | 69 |
| Failing | 0 | 0 |
| New Tests | — | 3 (Fact.match_key) |
