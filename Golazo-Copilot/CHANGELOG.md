# Changelog

## [1.1.5] - 2026-01-26

### Added
- Pattern Research Guide `.github/guides/PatternProposals.md` (GCP-012)
- 4-step pattern research process: SEARCH, COUNT, PRESENT, APPROVE
- Fail-Fast Rule for non-standard infrastructure patterns
- Spine reference to PatternProposals guide in Context-Specific Guides

## [1.1.4] - 2026-01-26

### Changed
- Updated all 10 role files to version 1.1.4 (GCP-011)
- Updated artifact paths in role files to use `WorkItems/` structure
- Standardized entry conditions with explicit redirect instructions

### Fixed
- Role file paths now consistent with spine artifact paths

## [1.1.3] - 2026-01-26

### Added
- Role Transition Announcement (MANDATORY) subsection in Operating mode (GCP-010)
- Requires explicit announcement when transitioning between roles
- Format: role names, reason for transition, artifact produced

## [1.1.2] - 2026-01-26

### Added
- Project Root Definition section with IDE-specific rules (GCP-009)
- Clear distinction between Repo Root and Project Root
- VS Code fallback with Project Owner confirmation

### Changed
- Removed all `<ProjectName>` tokens from artifact paths
- Artifact paths now explicitly relative to Project Root
- Directory structure diagram uses `<ProjectRoot>` instead of `<ProjectName>`

### Fixed
- Copilot file creation location confusion in multi-project repos

## [1.1.1] - 2026-01-22

### Added
- Fast-Track for Low-Risk Changes section (skip roles for config-only changes)
- Deployment & Infrastructure Changes section (5 guardrails for CI/CD work)

## [1.1.0] - 2026-01-22

### Added
- Technical guides directory `.github/guides/` (GCP-008)
- PowerShell terminal guide for encoding rules
- Golazo update guide for version checking and upgrades

### Changed
- Spine reduced from ~370 to ~240 lines by extracting technical guides
- Context-Specific Guides section replaces inline technical documentation
- Upgrade process now downloads 13 files (added 2 guide files)

### Improved
- GitHub Copilot interop: situational content loads only when relevant

## [1.0.11] - 2026-01-22

### Added
- Update detection and upgrade capability (GCP-007)
- Automatic version checking on session start (24-hour interval)
- Backup-before-upgrade workflow
- Manual update check via "check for Golazo updates"

## [1.0.0] - 2026-01-22

### Added
- Initial stable release
- Version metadata (GCP-006)
- Update detection (GCP-007)
