# Design Document: WIP-001 - Organize Photos by Date/Time

## Summary
A Python command-line tool that scans a source folder for photo files and copies them into a destination folder organized by year and month (`YYYY/MM/`) based on EXIF metadata or file modification date.

## Problem Statement
Users with large photo collections often have disorganized folders with photos from various dates mixed together. Manually sorting photos by date is tedious and error-prone. An automated solution reduces effort and ensures consistent organization.

## Business Case

### Why Now
- Photo collections grow continuously; the longer organization is delayed, the larger the backlog
- Foundation for WIP-002 (photo viewer) which depends on organized folder structure

### Impact
- Reduces manual photo organization time from hours to seconds
- Enables easier photo discovery by time period
- Preserves originals (copy operation) eliminating risk of data loss

### KPIs
| Metric | Target |
|--------|--------|
| Photos organized per second | > 15 photos/sec |
| Success rate (photos with valid dates) | > 95% for typical collections |
| User effort | Single command execution |

## Stakeholders
- **Primary**: Photo collection owners wanting automated organization
- **Secondary**: WIP-002 (viewer) depends on this folder structure

## Functional Requirements
| ID | Requirement |
|----|-------------|
| FR-1 | Accept source folder path as input |
| FR-2 | Accept destination folder path as input |
| FR-3 | Scan source folder recursively for photo files |
| FR-4 | Support JPG, JPEG, PNG, GIF, BMP formats |
| FR-5 | Extract date from EXIF metadata (DateTimeOriginal preferred) |
| FR-6 | Fall back to file modification date if EXIF unavailable |
| FR-7 | Copy photos to `destination/YYYY/MM/` structure |
| FR-8 | Skip non-photo files with warning |
| FR-9 | Display summary (processed, skipped, elapsed time) |

## Non-Functional Requirements
| ID | Requirement |
|----|-------------|
| NFR-1 | Handle 1000+ photos without crashing |
| NFR-2 | Complete 1000 photos in < 60 seconds |
| NFR-3 | Python 3.8+ compatibility |
| NFR-4 | Minimal dependencies (Pillow only for EXIF) |

## Proposed Approach

### High-Level Design
```
???????????????????     ????????????????????     ???????????????????
?  Source Folder  ???????  Photo Organizer ??????? Destination     ?
?  (flat/nested)  ?     ?                  ?     ? YYYY/MM/        ?
???????????????????     ????????????????????     ???????????????????
                               ?
                        ???????????????
                        ?             ?
                   EXIF Reader   File Stats
                   (Pillow)      (fallback)
```

### Components
1. **Main Entry Point** (`photo_organizer.py`)
   - CLI argument parsing (argparse)
   - Orchestrates scanning and copying

2. **Photo Scanner**
   - Recursively finds photo files by extension
   - Filters supported formats

3. **Date Extractor**
   - Reads EXIF DateTimeOriginal via Pillow
   - Falls back to `os.path.getmtime()`

4. **File Copier**
   - Creates `YYYY/MM/` folders as needed
   - Copies files preserving names
   - Handles filename collisions (append counter)

### CLI Interface
```bash
python photo_organizer.py <source_folder> <destination_folder>
```

### Output Example
```
Scanning: /photos/unsorted
Organizing to: /photos/organized

Processing... 
  Copied: IMG_001.jpg -> 2024/01/IMG_001.jpg
  Copied: IMG_002.jpg -> 2024/01/IMG_002.jpg
  Skipped: document.pdf (unsupported format)
  Copied: IMG_003.png -> 2023/12/IMG_003.png

Summary:
  Photos organized: 3
  Files skipped: 1
  Elapsed time: 0.5s
```

## Alternatives Considered

| Alternative | Pros | Cons | Decision |
|-------------|------|------|----------|
| Move instead of copy | Saves disk space | Risk of data loss | Rejected - safety first |
| GUI interface | More user-friendly | More complex, dependencies | Rejected - CLI for MVP |
| Database for tracking | Better duplicate detection | Overkill for MVP | Rejected - future enhancement |
| YYYY/MM/DD structure | More granular | Too many empty folders | Rejected |

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Pillow not installed | Medium | High | Clear error message with install instructions |
| Corrupted EXIF data | Low | Low | Fallback to file date |
| Filename collision in destination | Medium | Medium | Append counter (e.g., `IMG_001_2.jpg`) |
| Very large files slow copy | Low | Low | Acceptable for MVP; streaming copy |

## Open Questions
- None blocking for MVP

## Dependencies
| Dependency | Version | Purpose |
|------------|---------|---------|
| Python | >= 3.8 | Runtime |
| Pillow | >= 9.0 | EXIF metadata extraction |

## Migration / Rollout Plan
1. User installs Pillow: `pip install Pillow`
2. User runs: `python photo_organizer.py <source> <dest>`
3. No migration needed; creates new organized structure

## Rollback Plan
- Delete destination folder if results unsatisfactory
- Original photos untouched (copy operation)

## Observability Plan
- Console output during processing (verbose mode implicit)
- Summary statistics at completion
- Warning messages for skipped files

## Test Strategy Summary
1. **Unit tests**: Date extraction, path building, filename collision handling
2. **Integration tests**: End-to-end with sample photos (with/without EXIF)
3. **Edge cases**: Empty folders, nested folders, unsupported files, missing EXIF
