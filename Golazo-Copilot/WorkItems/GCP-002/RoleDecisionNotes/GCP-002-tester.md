# GCP-002: Tester Decision Document

## Work Item
GCP-002 — Golazo CLI Tool and README Documentation

## Decisions Made

### 1. pytest Over unittest
Using `pytest` for cleaner syntax and better fixtures.

**Rationale**: pytest is the de facto standard for Python testing; simpler assertions; better output.

### 2. Real Filesystem Over Mocks
Using `tempfile.TemporaryDirectory` instead of mocking `pathlib`/`os`.

**Rationale**: 
- Tests are more realistic
- Less brittle (don't break if implementation changes)
- `tempfile` is standard library

### 3. Skip Permission Tests on Windows
Windows permission model differs from Unix; skip TC-012 on Windows.

**Rationale**: Cross-platform testing complexity not worth it for edge case.

### 4. Test File in `tests/` Directory
Test file at `tests/test_golazo_copilot.py`.

**Rationale**: Standard Python project layout.

## Alternatives Considered

| Alternative | Rejected Because |
|-------------|------------------|
| Mock filesystem | More brittle; less realistic |
| unittest module | More verbose; less readable |
| No tests for README | README is a deliverable; should be verified |

## Tradeoffs Accepted

- Some tests require actual git repo structure (slower but more accurate)
- Permission tests skipped on Windows (coverage gap acceptable)

## Known Limitations or Risks

- Tests depend on source `.github/` files existing (not isolated)
- No coverage measurement in v1

## Test Execution Command

```bash
pytest tests/test_golazo_copilot.py -v
```
