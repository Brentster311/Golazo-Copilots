# GCP-007: Developer Notes

**Work Item**: GCP-007 - Golazo Copilot Update Detection and Upgrade  
**Date**: 2026-01-22

## Implementation Summary

GCP-007 is primarily a documentation change - adding instructions to the spine file that tell Copilot how to detect and perform updates.

### Changes Made

1. **Added "Golazo Update Check (GCP-007)" section to spine file**
   - Location: End of `.github/copilot-instructions.md`
   - Contains instructions for Copilot to:
     - Check for updates (when and how)
     - Compare versions
     - Display update availability to user
     - Perform backup and upgrade

### Key Implementation Details

- **Check trigger**: On session start if >24h since last check
- **Version source**: `https://raw.githubusercontent.com/Brentster311/Golazo-Copilots/main/Golazo-Copilot/VERSION`
- **Timestamp storage**: `.github/.golazo-update-check`
- **Backup location**: `.github/backup/<timestamp>/`
- **Download method**: PowerShell `Invoke-WebRequest`

### Files Modified
- `Golazo-Copilot/.github/copilot-instructions.md` - Added update check section

### Dependencies Completed
- GCP-006 (Versioning) - VERSION file, CHANGELOG.md, version comments all in place

## Testing Notes
- Manual testing required (Copilot behavior)
- Automated tests verify VERSION and CHANGELOG in package
- Network tests would require mocking GitHub
