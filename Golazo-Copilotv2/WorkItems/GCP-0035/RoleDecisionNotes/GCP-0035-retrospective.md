# GCP-0035 — Retrospective

## What went well
- Clear review identified exactly what was wrong (7 correctness + 5 completeness issues)
- Selective rewrite approach preserved accurate sections while fixing obsolete ones
- Grep-based test cases were fast and effective for documentation validation

## What didn't go well
- README drifted significantly over 10+ work items without being updated — the DoR/DoD → output validation pivot touched many features but README wasn't updated incrementally

## Action items
- Consider adding a "README accuracy check" to the documentor role instructions so README claims are cross-referenced after each feature change
- Future work items that change user-facing behavior should include "Update README" as an explicit acceptance criterion

## Metrics
- Zero stale references in README (verified by grep)
- All 5 actual tools documented
- All 4 new features covered
