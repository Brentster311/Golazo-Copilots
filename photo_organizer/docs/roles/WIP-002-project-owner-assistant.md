# Project Owner Assistant Notes: WIP-002

## Work Item
WIP-002 - View Organized Photos by Timeline

## Decisions Made

1. **Depends on WIP-001 folder structure**
   - Viewer expects `YYYY/MM/` organization
   - Can work independently if user manually organizes folders

2. **Chose tkinter for GUI**
   - Built into Python standard library
   - No external dependencies
   - Cross-platform (Windows, Mac, Linux)

3. **Simple single-image view with navigation**
   - MVP approach; more complex views (grid, slideshow) can come later
   - Previous/next navigation is intuitive

## Alternatives Considered

| Decision | Alternative | Why Rejected |
|----------|-------------|--------------|
| tkinter | PyQt/PySide | External dependency; overkill for simple viewer |
| tkinter | Web-based (Flask) | More complex setup; overkill for local viewing |
| Single image view | Thumbnail grid | More complex; can be added as future enhancement |

## Tradeoffs Accepted
- tkinter has dated appearance but is dependency-free
- Single image view is less efficient for browsing than thumbnails
- No caching means repeated image loading

## Known Limitations
- tkinter's image handling is basic; very large images may be slow
- No thumbnail generation (future enhancement)

## Risks
- LOW: tkinter availability (included with most Python installations)
- LOW: Pillow dependency for image loading (same as WIP-001)
