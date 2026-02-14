# EES-00014 — Retrospective

## What went well
- Clean removal: -259 lines net across 13 files
- Zero test regressions (258 passing)
- Systematic approach: models → extractor → GUI → tests
- `because` and `set_root_cause` references completely eliminated from src/ and tests/

## What didn't go well
- The conversation summary from prior sessions contained stale context claiming these were "current features" even though the user had apparently decided to remove them. This caused confusion when the AI referenced them.
- `gap_detector.py` was initially missed — found via a final grep sweep

## Action items
1. Always run a final `grep_search` sweep for removed identifiers across ALL source directories before running tests
2. The Capability-Impact.md naming convention issue recurred (file must be prefixed with work item ID)

## Metrics
- 10 tests removed (because/root_cause specific) + 258 passing = clean
