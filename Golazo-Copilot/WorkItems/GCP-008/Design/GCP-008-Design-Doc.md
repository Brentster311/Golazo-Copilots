# GCP-008: Design Document

## Summary

Extract PowerShell terminal rules (lines 216-260) and Golazo Update logic (lines 263-367) from the spine (`copilot-instructions.md`) into dedicated guide files in a new `.github/guides/` directory. This reduces the always-loaded spine by ~130 lines while maintaining all functionality through explicit references.

## Problem Statement

The current spine file is ~370 lines, but approximately 130 lines (~35%) are situationally relevant:
- **PowerShell rules (45 lines)**: Only needed when terminal operations are performed
- **Golazo Update logic (80 lines)**: Only needed when checking/performing updates

GitHub Copilot loads the spine for every interaction, consuming context window tokens with content that may not be relevant to the current task.

## Business Case

### Why Now
- Spine has grown with GCP-006 (version metadata) and GCP-007 (update capability)
- Context efficiency matters for Copilot quality
- Clean extraction point before further growth

### Impact
- Reduced context consumption for non-terminal, non-update workflows
- Clearer separation of concerns (workflow vs. technical guides)
- Easier maintenance of technical content

### KPIs
- Spine reduced from ~370 to ~240 lines
- Two focused guide files created
- All workflow behavior unchanged

## Stakeholders

- **Project Owner**: Approves structural changes
- **Golazo Users**: Benefit from improved Copilot responsiveness
- **Maintainers**: Easier to update technical guides independently

## Functional Requirements

### FR-1: Create PowerShell Terminal Guide
- File: `.github/guides/powershell-terminal.md`
- Content: All PowerShell/encoding rules from spine lines 216-260
- Version header: `<!-- Golazo Version: 1.1.0 -->`
- Self-contained with "When to use" section

### FR-2: Create Golazo Update Guide
- File: `.github/guides/golazo-update.md`
- Content: All update logic from spine lines 263-367
- Version header: `<!-- Golazo Version: 1.1.0 -->`
- Self-contained with "When to use" section

### FR-3: Update Spine with References
- Remove extracted content (lines 216-367)
- Add new "Context-Specific Guides" section with:
  - Reference to PowerShell guide with activation triggers
  - Reference to Update guide with activation triggers
- Update version header to `<!-- Golazo Version: 1.1.0 -->`

### FR-4: Update Upgrade Process
- Add guide files to "Files Downloaded During Upgrade" list
- Update backup commands to include guides directory
- Update download commands to include guide files

### FR-5: Update Version Files
- `Golazo-Copilot/VERSION`: Update to `1.1.0`
- `Golazo-Copilot/CHANGELOG.md`: Add GCP-008 entry

## Non-functional Requirements

- Guide files must be usable without reading spine first
- Extraction must be clean (no partial duplication)
- All existing tests must pass

## Proposed Approach

### Phase 1: Create Guide Files
1. Create `.github/guides/` directory
2. Create `powershell-terminal.md` with extracted content + "When to use" header
3. Create `golazo-update.md` with extracted content + "When to use" header

### Phase 2: Update Spine
1. Remove lines 216-367 (PowerShell + Update sections)
2. Insert new "Context-Specific Guides" section after "Safety and quality rules"
3. Update version header to 1.1.0

### Phase 3: Update Meta Files
1. Update `Golazo-Copilot/VERSION` to `1.1.0`
2. Add GCP-008 entry to `Golazo-Copilot/CHANGELOG.md`

### New Spine Structure (after refactor)
```
Lines 1-215: Unchanged (workflow, gates, artifacts, state machine)
Lines ~216-230: NEW "Context-Specific Guides" section
  - Reference to powershell-terminal.md
  - Reference to golazo-update.md
```

### New Directory Structure
```
.github/
??? copilot-instructions.md      # Spine (~240 lines, down from ~370)
??? roles/                       # Unchanged
?   ??? [10 role files]
??? guides/                      # NEW
    ??? powershell-terminal.md   # ~55 lines
    ??? golazo-update.md         # ~90 lines
```

## Alternatives Considered

| Alternative | Decision | Rationale |
|-------------|----------|-----------|
| Keep everything in spine | Rejected | Wastes context tokens on situational content |
| Extract to separate repo | Rejected | Adds complexity; guides are part of Golazo |
| Use include/import mechanism | Rejected | No standard mechanism for markdown in Copilot |

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Copilot doesn't load guides when needed | Medium | Medium | Clear triggers in spine; test manually |
| Upgrade process misses guide files | Low | High | Update download list; test upgrade flow |
| Guides become stale vs spine | Low | Medium | Version headers; single maintainer |

## Dependencies

- None external
- Internal: GCP-007 upgrade logic must be updated within this work item

## Migration / Rollout Plan

1. All changes in single commit on feature branch
2. Test workflow manually before merge
3. Merge to main
4. Verify upgrade from 1.0.11 ? 1.1.0 works

## Rollback Plan

- Revert single commit
- Guides are additive; spine references are the only breaking change
- Clean rollback to 1.0.11 state

## Observability Plan

- Manual verification of workflow behavior
- Manual verification of Copilot loading guides when relevant

## Test Strategy Summary

1. **Structural tests**: Verify files exist with correct headers
2. **Content tests**: Verify spine no longer contains extracted content
3. **Reference tests**: Verify spine contains guide references
4. **Workflow tests**: Verify existing Golazo behavior unchanged
