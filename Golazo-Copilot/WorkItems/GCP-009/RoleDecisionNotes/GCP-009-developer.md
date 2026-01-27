# GCP-009: Developer Decision Document

## Work Item
GCP-009 — Clarify Project Root Definition for Cross-IDE Compatibility

## Implementation Summary

Updated the Golazo spine to include explicit Project Root definition and removed all ambiguous `<ProjectName>` tokens.

## Changes Made

### 1. Added Project Root Definition Section
- Inserted after "Role instruction loading rule" section
- Includes IDE-specific rules for Visual Studio and VS Code
- Documents VS Code fallback with confirmation requirement
- Explains Repo Root vs Project Root distinction
- Provides correct/incorrect path examples

### 2. Updated Artifact Paths
- Removed all `<ProjectName>` tokens from paths
- Changed `<ProjectName>/WorkItems/...` to `WorkItems/...`
- Updated directory structure diagram to use `<ProjectRoot>`

### 3. Updated Version Files
- `VERSION`: Updated to `1.1.2`
- `CHANGELOG.md`: Added GCP-009 entry

## Files Modified

| File | Change |
|------|--------|
| `.github/copilot-instructions.md` | Added Project Root Definition section, removed `<ProjectName>` tokens |
| `VERSION` | Updated to `1.1.2` |
| `CHANGELOG.md` | Added GCP-009 entry |

## Test Results

| Test | Result |
|------|--------|
| TC-01: Project Root Definition section exists | ? PASS |
| TC-02: Visual Studio rule present | ? PASS |
| TC-05: No `<ProjectName>` tokens | ? PASS |

## Decisions Made

1. **Used `<ProjectRoot>` in directory diagram**
   - More accurate than `<ProjectName>`
   - Consistent with new terminology

2. **Preserved existing structure**
   - Only changed path prefixes, not folder organization
   - Backward compatible

## Next Role
Proceed to **Refactor Expert**.
