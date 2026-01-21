# Project Owner Assistant Notes: WIP-003

## Work Item
WIP-003 - GUI Photo Organizer with Viewer

## Must-Ask Checklist Verification

| Question | Answer | Source |
|----------|--------|--------|
| Interface type | GUI | User explicitly stated |
| Target platform | Windows | User explicitly stated |
| Data persistence | Files (copy to folders) | Inherited from WIP-001 |
| User type | Non-technical | Assumed (reasonable default for GUI) |

## Decisions Made

1. **Combined organize + view into single GUI app**
   - Original request: "organize photos" AND "easy way to view"
   - GUI naturally supports both in one application
   - WIP-002 (CLI viewer) is superseded by this

2. **Chose tkinter for GUI framework**
   - Built into Python standard library
   - No external dependencies to install
   - Sufficient for MVP requirements
   - Cross-platform potential if needed later

3. **Reuse WIP-001 organize logic**
   - Core organization logic already implemented and tested
   - GUI wraps existing functionality
   - Avoids code duplication

4. **Folder browse dialogs (not manual entry)**
   - Non-technical users expect "Browse" buttons
   - Reduces errors from typos in paths
   - Standard Windows UX pattern

## Alternatives Considered

| Decision | Alternative | Why Rejected |
|----------|-------------|--------------|
| tkinter | PyQt/PySide | External dependency; overkill for MVP |
| tkinter | wxPython | External dependency |
| Combined app | Separate organizer + viewer | User wants single "easy" solution |
| Browse dialogs | Text entry fields | Less user-friendly for non-technical users |

## Tradeoffs Accepted
- tkinter has dated appearance (acceptable for MVP)
- Windows-only initially (can expand later)
- No thumbnail grid view (single image view for MVP)

## Known Limitations
- tkinter threading can be tricky for responsive UI
- Large images may load slowly

## Risks
- LOW: tkinter availability (included with Python on Windows)
- MEDIUM: UI responsiveness during large batch operations (mitigate with threading)

## Relationship to Other Work Items
- **WIP-001** (CLI): Reuse core organize logic
- **WIP-002** (CLI viewer): Superseded by this story
