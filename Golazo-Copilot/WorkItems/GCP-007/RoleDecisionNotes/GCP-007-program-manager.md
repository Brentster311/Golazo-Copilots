# GCP-007: Program Manager Notes

**Work Item**: GCP-007 - Golazo Copilot Update Detection and Upgrade  
**Date**: 2026-01-20

## Decisions Made

1. **Check interval**: Once per 24 hours
   - Balances awareness with not being annoying
   - Timestamp stored in `.github/.golazo-update-check`

2. **Backup location**: `.github/backup/<timestamp>/`
   - Timestamp format: `YYYYMMDD-HHMMSS`
   - Preserves user modifications if any

3. **Update source**: GitHub raw files from `main` branch
   - No authentication required
   - Simple URL pattern
   - Always gets latest released version

4. **User consent flow**:
   - Show: "Golazo v1.0.0 installed. v1.1.0 available."
   - Show: Relevant CHANGELOG entries
   - Ask: "Would you like to upgrade? (yes/no)"
   - Never auto-upgrade without explicit consent

5. **Download method**: PowerShell `Invoke-WebRequest`
   - Works on Windows (primary Visual Studio platform)
   - Could add `curl` fallback for cross-platform

## Sequencing Rationale

This work item depends on GCP-006:
- Cannot compare versions without version metadata
- Cannot show "what changed" without CHANGELOG

Sequence: GCP-006 ? GCP-007

## Operational Considerations

### Failure Modes
| Failure | User Experience | Recovery |
|---------|-----------------|----------|
| Network timeout | "Could not check for updates. Continuing normally." | User can retry later |
| Download fails mid-upgrade | Backup exists, user notified | Manual restore from backup |
| Parse error on VERSION | Treated as "up to date" | No action needed |

### Check Frequency Logic
```
IF .golazo-update-check exists:
    lastCheck = read timestamp from file
    IF (now - lastCheck) < 24 hours:
        SKIP check
    ELSE:
        PERFORM check
ELSE:
    PERFORM check
```

## Open Questions for Architect
1. Should we support macOS/Linux? (different shell commands)
2. Should backup retention be limited? (e.g., keep only 3 backups)
3. Should we add integrity verification? (checksums)

## Handoff to Reviewer/Architect
- Verify the update check instructions are safe and non-intrusive
- Confirm download URLs are correct
- Review backup strategy adequacy
