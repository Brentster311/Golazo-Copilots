# GCP-008: Developer Decision Document

## Work Item
GCP-008 — Extract Technical Guides from Spine for Improved Copilot Interop

## Implementation Summary

Successfully extracted ~130 lines of context-specific technical content from the spine into dedicated guide files.

## Files Created

| File | Purpose | Lines |
|------|---------|-------|
| `.github/guides/powershell-terminal.md` | PowerShell encoding rules and patterns | ~80 |
| `.github/guides/golazo-update.md` | Version checking and upgrade procedures | ~100 |

## Files Modified

| File | Change |
|------|--------|
| `.github/copilot-instructions.md` | Removed inline technical content, added "Context-Specific Guides" section with references |
| `VERSION` | Updated to `1.1.1` |
| `CHANGELOG.md` | Added GCP-008 entry |

## Decisions Made

1. **Created `.github/guides/` directory**
   - Follows existing `.github/roles/` pattern
   - Clear separation: roles = workflow participants, guides = technical references

2. **Guide file structure**
   - Each guide has "When to Use" section at top
   - Self-contained content (usable without spine context)
   - Version header for tracking

3. **Spine references**
   - Added "Context-Specific Guides" section at end of spine
   - Clear trigger conditions for when to load each guide

## Alternatives Considered

| Alternative | Rejected Because |
|-------------|------------------|
| Inline technical content | Bloats context window for non-terminal tasks |
| Single combined guide file | Less targeted loading |
| Automatic keyword detection | Over-engineering; explicit references sufficient |

## Tradeoffs Accepted

- Guides must be explicitly referenced (not auto-loaded)
- Slight increase in file count

## Known Limitations or Risks

- Copilot must recognize trigger conditions to load guides
- Users unfamiliar with guide locations may not know to reference them

## Test Results

- All acceptance criteria verified
- Spine correctly references guide files
- Guide files contain complete extracted content

## Next Role
Proceed to **Refactor Expert**.
