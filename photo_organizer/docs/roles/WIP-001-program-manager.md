# Program Manager Notes: WIP-001

## Work Item
WIP-001 - Organize Photos by Date/Time

## Decisions Made

1. **CLI-first approach**
   - Simple command-line interface using argparse
   - Aligns with "easy to use" requirement without GUI complexity
   - Can be wrapped in GUI later (WIP-002 provides viewing)

2. **Single-file implementation for MVP**
   - All logic in `photo_organizer.py`
   - Simple to understand, test, and deploy
   - Can refactor into modules if complexity grows

3. **Pillow for EXIF extraction**
   - Industry-standard Python imaging library
   - Well-maintained, cross-platform
   - Only external dependency needed

4. **Filename collision handling via counter suffix**
   - If `IMG_001.jpg` exists, use `IMG_001_2.jpg`
   - Preserves original filename for traceability
   - Simple and predictable

## Alternatives Considered

| Decision | Alternative | Why Rejected |
|----------|-------------|--------------|
| CLI | GUI (tkinter) | Adds complexity; viewer (WIP-002) handles GUI |
| Pillow | exifread library | Pillow is more widely used and maintained |
| Counter suffix | Timestamp suffix | Counter is simpler and more predictable |
| Single file | Multiple modules | Overkill for MVP scope |

## Tradeoffs Accepted
- No progress bar for MVP (verbose output sufficient)
- No configuration file (CLI args sufficient for MVP)
- No dry-run mode (can be added as future enhancement)

## Known Limitations
- No parallel processing (sequential copy is fast enough for MVP)
- No resume capability if interrupted

## Risks
- **LOW**: Pillow installation issues on some systems
  - Mitigation: Clear error message with install command

## Sequencing
1. Implement core logic (scan, extract date, copy)
2. Add CLI interface
3. Add error handling and edge cases
4. Test with sample photos

## Open Items Resolved
- Filename collision: Use counter suffix
- Nested source folders: Scan recursively
