# Changelog

All notable changes to Golazo Copilot will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-22

### Added
- Initial stable release of Golazo Copilot workflow
- Complete 10-role workflow: Project Owner Assistant, Program Manager, Reviewer, Architect, Tester, Developer, Refactor Expert, Builder, Documentor, Retrospective
- Definition of Ready (DoR) and Definition of Done (DoD) enforcement
- Golazo Status header requirement for every response
- Work item artifact structure with User Stories, Design Docs, Review Comments, Test Cases
- Role decision notes for audit trail
- `Golazo_Copilot.py` CLI tool for installation and packaging
- `--package` flag to create distributable zip files
- README.md with comprehensive documentation
- USAGE-VisualStudio.md and USAGE-VSCode.md guides
- Version metadata in all instruction files (GCP-006)

### Release Checklist
When releasing a new version:
1. Update VERSION file with new version number
2. Update version comment on line 1 of all MD files in `.github/`
3. Add new entry to this CHANGELOG
4. Run `python Golazo_Copilot.py --package` to create distribution
5. Test the distribution zip
6. Commit and tag release
