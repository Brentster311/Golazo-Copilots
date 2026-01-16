# User Story: WIP-002

**Status**: BACKLOG

## User Story

- **Title**: View Organized Photos by Timeline
- **As a**: Photo collection owner
- **I want**: A simple viewer to browse my organized photos by year and month
- **So that**: I can easily find and view photos from specific time periods

## Out of Scope
- Photo organization/sorting (handled by WIP-001)
- Photo editing capabilities
- Slideshow mode
- Sharing features
- Thumbnail caching

## Assumptions
- **Assumption (explicit)**: Photos are already organized in `YYYY/MM/` folder structure (from WIP-001)
- **Assumption (explicit)**: Simple GUI using tkinter (built-in, no extra dependencies)
- **Assumption (explicit)**: Single photo view with navigation (previous/next)
- **Assumption (explicit)**: Python 3.8+ with tkinter available

## Acceptance Criteria (bulleted, testable)
- [ ] User can select a root folder containing organized photos
- [ ] User can browse available years and months in a list/tree
- [ ] User can view photos from a selected year/month
- [ ] User can navigate between photos (previous/next buttons or arrow keys)
- [ ] Current photo filename and date are displayed

## Non-functional Requirements
- GUI must be responsive (not freeze during image loading)
- Images should scale to fit the window

## Telemetry / Metrics Expected
- None required for MVP

## Rollout / Rollback Notes
- Standalone viewer; no data changes
