# GCP-006: Design Document

## Summary
Add version metadata to all Golazo instruction files (spine and roles) to enable version identification and future update detection capabilities.

## Problem Statement
Currently, there is no way to identify which version of Golazo instructions are installed in a repository. Users cannot determine if their instructions are current, and there is no foundation for automated update detection.

## Business Case

### Why Now
- GCP-007 (update detection) depends on this capability
- As Golazo gains adoption, version drift becomes a real concern
- Users need confidence they're using the latest workflow improvements

### Impact
- Enables the entire update detection feature (GCP-007)
- Reduces support burden ("which version are you on?")
- Creates foundation for future compatibility management

### KPIs
- All 11 MD files (1 spine + 10 roles) contain version metadata
- VERSION file exists and matches spine version
- CHANGELOG.md documents at least current version

## Stakeholders
- **Golazo users**: Need to know their installed version
- **Golazo maintainers**: Need to track releases
- **GCP-007**: Depends on this for version comparison

## Functional Requirements
1. Spine file contains version comment: `<!-- Golazo Version: X.Y.Z -->`
2. Each role file contains matching version comment
3. `VERSION` file at repo root contains version string only
4. `CHANGELOG.md` at repo root documents changes per version
5. `Golazo_Copilot.py --package` includes VERSION and CHANGELOG.md

## Non-Functional Requirements
1. Version comments must not affect Copilot's parsing of instructions
2. Version format must be machine-readable (regex-extractable)
3. All versions must stay in sync across files

## Proposed Approach

### Phase 1: Add Version Infrastructure
1. Create `VERSION` file with content `1.0.0`
2. Create `CHANGELOG.md` with initial entry
3. Add `<!-- Golazo Version: 1.0.0 -->` to line 1 of spine file
4. Add same comment to line 1 of each role file

### Phase 2: Update Packaging
1. Modify `create_package()` in `Golazo_Copilot.py` to include VERSION and CHANGELOG.md

### File Changes
| File | Change |
|------|--------|
| `VERSION` | Create (new file) |
| `CHANGELOG.md` | Create (new file) |
| `.github/copilot-instructions.md` | Add version comment line 1 |
| `.github/roles/*.md` (10 files) | Add version comment line 1 |
| `Golazo_Copilot.py` | Update `create_package()` |

## Alternatives Considered

| Alternative | Pros | Cons | Decision |
|-------------|------|------|----------|
| YAML front matter | Structured | Some parsers render it | Rejected |
| Git tags only | Native to git | Not visible in files | Rejected |
| JSON manifest | Machine-friendly | Extra complexity | Rejected |
| **HTML comments** | Invisible in render, parseable | Slight maintenance burden | **Selected** |

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Version drift (files out of sync) | Medium | Low | Document release checklist |
| Comment breaks parsing | Low | High | Test with Copilot after change |
| Forgotten on release | Medium | Low | Add to release checklist in CHANGELOG |

## Dependencies
- None (this is a foundational work item)

## Migration / Rollout / Rollback Plan

### Rollout
1. Create VERSION and CHANGELOG.md files
2. Add version comments to all MD files
3. Update Golazo_Copilot.py packaging
4. Test with `--package` command
5. Commit to main branch

### Rollback
- Remove version comments (non-breaking, comments are ignored)
- Delete VERSION and CHANGELOG.md if needed

## Observability Plan
- N/A (documentation-only change, no runtime behavior)

## Test Strategy Summary
1. Verify VERSION file contains valid semver string
2. Verify all MD files contain matching version comment
3. Verify `--package` includes VERSION and CHANGELOG.md in zip
4. Verify Copilot still parses instructions correctly after changes
