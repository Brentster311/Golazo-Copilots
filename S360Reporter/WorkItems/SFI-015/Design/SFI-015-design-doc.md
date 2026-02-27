# SFI-015: Design Doc - Detail Page Color Indicators

**Status**: IN PROGRESS  
**Designer**: Program Manager  
**Date**: 2026-02-05

---

## Summary

Add colored circle indicators to section headers in the S360Reporter detail modal to match the visual design of the sidebar list view. This is a low-risk cosmetic fix that improves UI consistency.

---

## Problem Statement

The detail modal displays SFI action item information organized into sections (Status, Dates, Ownership, Service & Program), but the section headers lack the colored circle indicators present in the sidebar list view. This creates visual inconsistency and reduces scanability.

**Current behavior**: Labels appear as plain text  
**Expected behavior**: Labels have colored circles matching sidebar design (Status=🔴, Dates=🔵, Ownership=🟣, Service & Program=⚫)

---

## Business Case

- **Why now**: User reported inconsistency; low-hanging fruit for improved UX
- **Impact**: Better visual consistency; improved user scanning speed
- **KPI**: User satisfaction with detail view appearance (subjective; no metrics needed for cosmetic fix)
- **Effort**: ~30 minutes (copy + adapt existing sidebar code)

---

## Stakeholders

- **User**: End user viewing SFI details
- **Developer**: Will implement the fix
- **QA**: Will verify visual consistency
- **Product Owner**: S360Reporter team (approves cosmetic changes)

---

## Requirements

### Functional Requirements

1. Each section header in the detail modal shall display a colored circle indicator
2. Indicators shall match the sidebar list view color scheme:
   - Status → 🔴 (red)
   - Dates → 🔵 (blue)  
   - Ownership → 🟣 (purple)
   - Service & Program → ⚫ (gray/dark)
3. Indicators shall be rendered as Unicode emoji or similar tkinter-supported character
4. Detail modal shall render identically in popup and embedded modes

### Non-Functional Requirements

- No performance degradation
- Indicator rendering shall be consistent across Windows, Mac, Linux
- Font scaling shall not break indicator appearance

---

## Proposed Approach

### High-Level Solution

1. **Identify rendering code**: Locate detail modal header construction in `tk_app.py` (likely `DetailWindow` class or modal builder function)
2. **Copy sidebar pattern**: Extract the colored circle rendering logic from the sidebar list view
3. **Apply to details**: Update detail modal header labels to include the emoji prefix (e.g., "🔴 Status" instead of "Status")
4. **Test**: Verify all sections render correctly in both popup and embedded modes

### Implementation Outline

**Step 1: Sidebar Code Reference**  
Search `tk_app.py` for existing colored indicator patterns. Expected to find something like:
```python
"🔴 Status"  # or similar emoji/character approach
```

**Step 2: Detail Modal Update**  
Find detail modal construction (likely `DetailWindow.__init__()` or similar) and update header label formatting to include emoji.

**Step 3: Testing**  
- [ ] Open detail modal and verify all sections have colored circles
- [ ] Test in both popup (click item) and embedded (if applicable) modes
- [ ] Verify colors match sidebar exactly

---

## Alternatives Considered

| Alternative | Pros | Cons | Verdict |
|------------|------|------|---------|
| Use Unicode escapes (e.g., `\u1F534`) | More portable | Harder to read in code | ❌ |
| Use tkinter color codes directly | Native support | Requires more refactoring | ❌ |
| Add SVG/image indicators | Professional look | Adds file dependencies | ❌ |
| Copy emoji approach from sidebar | Minimal change, proven pattern | Limited by emoji font support | ✅ **CHOSEN** |

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Emoji rendering differs on some systems | Visual inconsistency on Linux/Mac | Test on all platforms before merge; fall back to ASCII if needed |
| Detail modal becomes unresponsive | User experience degraded | Implement rendering in background thread if needed; profile first |
| Color scheme conflicts with dark mode | Indicators invisible | Test with both light and dark themes; use high-contrast colors |

---

## Dependencies

- None (implementation is self-contained within `tk_app.py`)

---

## Migration / Rollout / Rollback Plan

### Rollout
1. Merge PR to `main` branch
2. Include in next S360Reporter release (v0.2.1 or v0.3.0)
3. No user action required; update is automatic

### Rollback
If visual issues arise post-merge:
1. Revert commit: Remove emoji characters from detail modal header labels
2. Publish patch release
3. Root cause: Unicode font rendering on specific OS

No data migration or user communication needed.

---

## Observability Plan

- **Logs**: No special logging needed
- **Metrics**: None (cosmetic change)
- **Errors**: If rendering fails, tkinter will raise warnings; monitor Windows Event Viewer (Windows) or syslog (Linux/Mac)

---

## Test Strategy Summary

### Unit Testing
- N/A (UI rendering; manual testing preferred)

### Integration Testing
1. Open detail modal for various SFI items
2. Verify all section headers (Status, Dates, Ownership, Service & Program) display colored circles
3. Verify colors match sidebar list view
4. Test on Windows (primary platform)

### Regression Testing
- Verify detail modal still displays all information correctly
- Verify modal can still be closed/resized/dragged
- Verify other UI elements are not affected

### Cross-Platform Testing (lower priority)
- Test on Mac and Linux if time permits
- If emoji rendering fails, document fallback approach

---

## Open Questions

1. Should the Streamlit web app (`flet_app.py`) also be updated? (Out of scope for this story, but noted for future)
2. Are there any accessibility concerns with emoji rendering? (Should be addressed in separate story if needed)

---

## Success Metrics

- ✅ Detail modal section headers display colored indicators
- ✅ Colors match sidebar list view exactly
- ✅ No performance degradation
- ✅ User confirms visual consistency is improved

---

## Appendix

### Related Files
- `GUI/src/sfi_reporter/tk_app.py` (DetailWindow, modal builder)
- `GUI/src/sfi_reporter/flet_app.py` (Flet version, out of scope)

### References
- SFI-014: Previous modal fix (for context on similar work)
- Sidebar list rendering (model for colored indicators)
