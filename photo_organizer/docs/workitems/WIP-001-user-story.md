# User Story: WIP-001

**Status**: BACKLOG

## User Story

- **Title**: Organize Photos by Date/Time
- **As a**: Photo collection owner
- **I want**: To scan a folder of photos and organize them into subfolders by date (year/month)
- **So that**: My photos are automatically sorted chronologically without manual effort

## Out of Scope
- Viewing/browsing photos (separate story WIP-002)
- Duplicate detection
- Photo editing or metadata modification
- Cloud storage integration
- Video file handling

## Assumptions
- **Assumption (explicit)**: Photos are in common formats (JPG, JPEG, PNG, GIF, BMP)
- **Assumption (explicit)**: Date is extracted from EXIF metadata; if unavailable, file modification date is used as fallback
- **Assumption (explicit)**: Organized photos are copied (not moved) to preserve originals
- **Assumption (explicit)**: Output folder structure is `YYYY/MM/` (e.g., `2024/01/`)
- **Assumption (explicit)**: Python 3.8+ is the target runtime

## Acceptance Criteria (bulleted, testable)
- [ ] User can specify a source folder containing photos
- [ ] User can specify a destination folder for organized output
- [ ] Photos are copied into `YYYY/MM/` subfolders based on date taken
- [ ] If EXIF date is missing, file modification date is used
- [ ] Unsupported file types are skipped with a warning message
- [ ] A summary is displayed showing count of photos organized

## Non-functional Requirements
- Must handle folders with 1000+ photos without crashing
- Should complete within reasonable time (< 1 minute for 1000 photos on typical hardware)

## Telemetry / Metrics Expected
- Count of photos processed
- Count of photos skipped (no valid date or unsupported format)
- Elapsed time

## Rollout / Rollback Notes
- No rollback needed; original photos are preserved (copy, not move)
