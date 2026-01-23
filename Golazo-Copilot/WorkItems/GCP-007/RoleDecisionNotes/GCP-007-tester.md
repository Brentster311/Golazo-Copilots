# GCP-007: Tester Notes

**Work Item**: GCP-007 - Golazo Copilot Update Detection and Upgrade  
**Date**: 2026-01-20

## Decisions Made

1. **Test approach**: Mix of automated and manual tests
   - Automated: File operations, version comparison logic
   - Manual: Copilot behavior verification

2. **Coverage**: All 8 acceptance criteria have mapped test cases

3. **Edge cases included**:
   - Invalid remote version format
   - Local newer than remote (no downgrade)
   - Permission denied
   - Partial download failure

## Test Strategy

### Automated Tests
- PowerShell scripts for network operations
- File system verification for backup/download
- Version comparison logic unit tests

### Manual Tests
- Copilot session behavior
- Changelog display formatting
- User prompt interaction

## Tradeoffs Accepted

1. **Cannot fully automate Copilot tests**
   - Copilot behavior requires manual verification
   - Document expected behavior for tester to verify

2. **Network tests may be flaky**
   - Depend on GitHub availability
   - Mark as "integration" tests, run separately

## Known Limitations

- Manual tests required for full Copilot behavior verification
- Network tests require internet access
- Timestamp manipulation may need system clock changes or mocking

## Test Implementation Plan

1. Create version comparison utility (can be unit tested)
2. Create backup/restore verification script
3. Document manual test procedures for Copilot interaction
4. Create test fixtures (old VERSION, new VERSION, CHANGELOG)
