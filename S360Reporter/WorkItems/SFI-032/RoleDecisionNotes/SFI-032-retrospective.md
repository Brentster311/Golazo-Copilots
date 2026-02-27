# SFI-032 Retrospective

## What went well
- TDD cycle was clean: 6 tests written → 3 failed as expected → implementation made all 6 pass
- The refactor was surgical: moved cache code without changing behaviour
- Test isolation fix (`cache_enabled=False` in base fixture) was caught immediately

## What didn't go well
- Cross-test contamination was not anticipated — the default `S360Config(cache_enabled=True)` caused existing tests to share a real system cache directory
- Terminal CWD management was fragile during test runs

## Action items
- When adding caching to a class, always ensure test fixtures disable caching by default unless testing cache specifically
- Consider adding `cache_enabled=False` to `S360Config` defaults (SDK shouldn't cache by default — consumers opt in)

## Metrics
- Lines removed from services.py: ~110
- Lines added to graph.py: ~115
- Net test count: 76 SDK + 4 S360Reporter (was 76 + 11, now more focused)
