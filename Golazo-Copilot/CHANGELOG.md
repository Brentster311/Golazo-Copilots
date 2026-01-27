# Changelog

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
