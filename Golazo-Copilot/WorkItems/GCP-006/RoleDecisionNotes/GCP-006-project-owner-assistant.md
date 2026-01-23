# GCP-006: Project Owner Assistant Notes

**Work Item**: GCP-006 - Add Versioning to Golazo Instruction Files  
**Date**: 2026-01-20

## Decisions Made

1. **Version format**: Semantic versioning (MAJOR.MINOR.PATCH)
   - Industry standard, well-understood
   - Allows communicating breaking vs non-breaking changes

2. **Version location in MD files**: HTML comment format `<!-- Golazo Version: X.Y.Z -->`
   - Does not render in markdown viewers
   - Does not interfere with Copilot's instruction parsing
   - Can be extracted programmatically via regex

3. **Separate VERSION file**: Plain text file at repo root
   - Easy to fetch via raw GitHub URL
   - Single source of truth for current version
   - Simplifies comparison logic in GCP-007

4. **CHANGELOG.md**: Standard changelog at repo root
   - Allows users to see what changed before upgrading (per GCP-007 requirement)
   - Follows Keep a Changelog format

5. **Initial version**: 1.0.0
   - Golazo is already functional and in use
   - Starting at 1.0.0 indicates production readiness

## Alternatives Considered

| Alternative | Why Rejected |
|-------------|--------------|
| YAML front matter | Some markdown parsers render it; less universal |
| JSON metadata file | Extra file complexity; not human-readable at glance |
| Git tags only | Requires git access; not visible in installed files |
| Version in filename | Would require renaming files on every release |

## Tradeoffs Accepted
- Adding comments to every role file increases maintenance burden slightly
- Must remember to update VERSION and all MD files together on release

## Known Limitations
- Version in MD files could become stale if manually edited by user
- No cryptographic verification of file integrity (out of scope)

## Dependencies
- This work item enables GCP-007 (update detection)
