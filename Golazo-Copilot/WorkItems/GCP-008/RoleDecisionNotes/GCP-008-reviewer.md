# GCP-008 - Reviewer Decision Notes

## Work Item
GCP-008: Extract Technical Guides from Spine for Improved Copilot Interop

## Decisions Made

1. **Approved design with minor clarifications**: No scope/behavior changes needed
2. **Identified upgrade script gaps**: Directory creation and backup for guides
3. **Classified as non-functional clarifications**: Both issues are implementation details, not scope changes

## Alternatives Considered

| Alternative | Decision | Rationale |
|-------------|----------|-----------|
| Require separate story for upgrade fixes | Rejected | These are clarifications to the existing upgrade logic, not new features |
| Ignore directory creation issue | Rejected | Would cause upgrade failures on fresh repos |

## Tradeoffs Accepted

- Adding `-ErrorAction SilentlyContinue` to guide backup means silent failure if guides don't copy, but this is acceptable for backward compatibility

## Known Limitations

- Cannot test upgrade path from every possible prior version
- Relying on `-Force` and `-ErrorAction SilentlyContinue` for robustness

## Risks

| Risk | Mitigation |
|------|------------|
| Upgrade fails on directory creation | Explicitly create directory with `-Force` |
| Guides not backed up | Add backup line; silent continue for repos without guides |
