# GCP-008 - Developer Decision Notes

## Work Item
GCP-008: Extract Technical Guides from Spine for Improved Copilot Interop

## Decisions Made

1. **Created `.github/guides/` directory**: New directory for technical guides
2. **Created `powershell-terminal.md`**: 85 lines with "When to Use" section and all PowerShell rules
3. **Created `golazo-update.md`**: 130 lines with "When to Use" section and complete update process
4. **Updated spine**: Removed 153 lines, added 17-line "Context-Specific Guides" section
5. **Version bump**: 1.0.11 ? 1.1.0

## Implementation Details

### Files Created
- `Golazo-Copilot/.github/guides/powershell-terminal.md`
- `Golazo-Copilot/.github/guides/golazo-update.md`

### Files Modified
- `Golazo-Copilot/.github/copilot-instructions.md` (version header + content replacement)
- `Golazo-Copilot/VERSION` (1.0.11 ? 1.1.0)
- `Golazo-Copilot/CHANGELOG.md` (added 1.1.0 entry)

### Line Count Changes
| File | Before | After | Change |
|------|--------|-------|--------|
| Spine | 367 | 229 | -138 |
| PowerShell Guide | N/A | 85 | +85 |
| Update Guide | N/A | 130 | +130 |

## Alternatives Considered

| Alternative | Decision | Rationale |
|-------------|----------|-----------|
| Keep extracted content identical | Modified | Added "When to Use" sections for self-containment |
| Minimal guide files | Rejected | Self-contained guides are more useful |

## Tradeoffs Accepted

- Total lines increased (367 ? 444) but context efficiency improved (229 always-loaded)

## Known Limitations

- Path issue during development (files initially created in nested directory) - corrected

## Test Results

| Test ID | Result | Notes |
|---------|--------|-------|
| TC-001 | ? Pass | PowerShell guide exists with v1.1.0 header |
| TC-002 | ? Pass | Update guide exists with v1.1.0 header |
| TC-003 | ? Pass | Spine reduced to 229 lines, no extracted content |
| TC-004 | ? Pass | VERSION=1.1.0, CHANGELOG has entry |
| TC-005 | ? Pass | Guides listed in upgrade process |
