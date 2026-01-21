# User Story: WIP-003

**Status**: BACKLOG

## User Story

- **Title**: GUI Photo Organizer with Viewer
- **As a**: Photo collection owner (non-technical user)
- **I want**: A graphical application to organize my photos by date and browse them
- **So that**: I can easily manage and view my photo collection without using command line

## Out of Scope
- Cloud storage integration
- Photo editing or metadata modification
- Duplicate detection
- Video file handling
- Mac/Linux support (Windows only for MVP)

## Assumptions
- **Assumption (explicit)**: Windows target platform
- **Assumption (explicit)**: tkinter for GUI (built-in, no extra dependencies)
- **Assumption (explicit)**: Non-technical users (folder browse dialogs, no manual path entry required)
- **Assumption (explicit)**: Reuses existing organize logic from WIP-001
- **Assumption (explicit)**: Photos are in common formats (JPG, JPEG, PNG, GIF, BMP)
- **Assumption (explicit)**: Python 3.8+ is the target runtime

## Acceptance Criteria (bulleted, testable)
- [ ] Application launches with a main window
- [ ] User can browse to select source folder via dialog
- [ ] User can browse to select destination folder via dialog
- [ ] User can click "Organize" button to start organization
- [ ] Progress is displayed during organization
- [ ] Summary is shown when organization completes
- [ ] User can browse organized photos by year/month in a tree view
- [ ] User can view selected photo in the application

## Non-functional Requirements
- Window should be resizable
- Should not freeze during long operations (responsive UI)
- Should work on Windows 10/11

## Telemetry / Metrics Expected
- Count of photos organized (displayed in summary)
- Count of photos skipped (displayed in summary)

## Rollout / Rollback Notes
- Standalone application; no installation required
- No rollback needed; original photos preserved (copy operation)
