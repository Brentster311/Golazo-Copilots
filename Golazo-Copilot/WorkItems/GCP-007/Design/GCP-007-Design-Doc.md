# GCP-007: Design Document

## Summary
Enable Golazo Copilot to detect when a newer version of instructions is available on GitHub and offer to upgrade the local installation, showing the user what changed before they decide.

## Problem Statement
Users who install Golazo instructions have no way to know when updates are available. They must manually check the GitHub repository, compare versions, and download files. This friction means users run outdated instructions and miss workflow improvements.

## Business Case

### Why Now
- GCP-006 (versioning) enables this feature
- Golazo is gaining adoption; keeping users current is critical
- Manual update checking doesn't scale

### Impact
- Users always know when updates are available
- Reduced support requests about outdated behavior
- Faster adoption of workflow improvements

### KPIs
- Copilot successfully detects version mismatch
- User sees changelog before deciding
- Upgrade completes without corrupting files

## Stakeholders
- **Golazo users**: Want to stay current with minimal effort
- **Golazo maintainers**: Want users on latest version
- **Project Owner**: Must approve upgrade (consent-based)

## Functional Requirements
1. Copilot checks remote VERSION file from `https://raw.githubusercontent.com/Brentster311/Golazo-Copilots/main/VERSION`
2. Copilot extracts local version from spine file comment
3. If remote > local, Copilot displays: current version, new version, relevant changelog
4. Copilot asks user for confirmation before any file changes
5. If user confirms:
   - Backup existing `.github/` files to `.github/backup/<timestamp>/`
   - Download all instruction files from GitHub main branch
   - Report success with new version number
6. Track "last checked" timestamp to avoid repeated checks
7. If network fails, report gracefully and continue normal operation

## Non-Functional Requirements
1. Update check must not block user workflow
2. Network timeout: 5 seconds max
3. Backup must complete before any overwrites
4. Check interval: Once per day (not every session)

## Proposed Approach

### Phase 1: Add Version Check Instructions to Spine
Add a new section to `.github/copilot-instructions.md` that instructs Copilot:
- When to check (session start, if >24h since last check)
- How to check (fetch remote VERSION via `get_web_pages` or terminal)
- How to compare versions
- What to display to user
- How to get consent

### Phase 2: Add Upgrade Instructions to Spine
Instructions for Copilot to:
- Create backup directory
- Download files via PowerShell `Invoke-WebRequest`
- Verify downloads succeeded
- Report completion

### Files to Download During Upgrade
```
.github/copilot-instructions.md
.github/roles/project-owner-assistant.md
.github/roles/program-manager.md
.github/roles/reviewer.md
.github/roles/architect.md
.github/roles/tester.md
.github/roles/developer.md
.github/roles/refactor-expert.md
.github/roles/builder.md
.github/roles/documentor.md
.github/roles/retrospective.md
```

### Last Checked Timestamp Storage
- Store in `.github/.golazo-update-check` (hidden file)
- Format: ISO 8601 timestamp
- Created/updated by Copilot after each check

### URLs (GitHub Raw)
- VERSION: `https://raw.githubusercontent.com/Brentster311/Golazo-Copilots/main/VERSION`
- CHANGELOG: `https://raw.githubusercontent.com/Brentster311/Golazo-Copilots/main/CHANGELOG.md`
- Spine: `https://raw.githubusercontent.com/Brentster311/Golazo-Copilots/main/.github/copilot-instructions.md`
- Roles: `https://raw.githubusercontent.com/Brentster311/Golazo-Copilots/main/.github/roles/<filename>`

## Alternatives Considered

| Alternative | Pros | Cons | Decision |
|-------------|------|------|----------|
| Azure Artifacts | Enterprise-grade | Complex auth, overkill | Rejected |
| GitHub Releases API | Professional | Complex JSON parsing | Rejected |
| Python script update | Reliable | Script not always installed | Rejected |
| **GitHub raw files** | Simple, no auth | Requires internet | **Selected** |

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| GitHub unreachable | Low | Low | Graceful timeout, continue normally |
| Download corruption | Low | Medium | Backup before overwrite |
| User has local modifications | Medium | Medium | Backup preserves their changes |
| Version comparison fails | Low | Low | Treat as "up to date" on error |

## Dependencies
- **GCP-006**: Must be complete (version metadata in files)

## Migration / Rollout / Rollback Plan

### Rollout
1. Complete GCP-006 first
2. Add update-check section to spine
3. Test with deliberate version mismatch
4. Verify backup and download work correctly

### Rollback
- Remove update-check section from spine
- Copilot reverts to no update awareness

## Observability Plan
- N/A (runs locally, no server-side telemetry)

## Test Strategy Summary
1. **Version detection**: Mock remote VERSION higher than local, verify Copilot detects
2. **Changelog display**: Verify CHANGELOG is fetched and relevant section shown
3. **Backup creation**: Verify backup directory created with timestamp
4. **Download success**: Verify all 11 files downloaded correctly
5. **Timestamp tracking**: Verify `.golazo-update-check` file created/updated
6. **Network failure**: Verify graceful handling when GitHub unreachable
