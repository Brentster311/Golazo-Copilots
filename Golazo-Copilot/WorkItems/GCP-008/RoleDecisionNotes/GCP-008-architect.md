# GCP-008 - Architect Notes

## Architectural Review

### Alignment and Boundaries

? **Correct boundary**: Technical guides separated from workflow logic
? **Consistent pattern**: Guides parallel roles (`.github/guides/` mirrors `.github/roles/`)
? **Single responsibility**: Each guide has one focus area

### Contracts and Interfaces

#### File Contract: Guide Files
```markdown
<!-- Golazo Version: X.Y.Z -->
# [Guide Title]

## When to Use
[Clear activation triggers]

## [Content sections]
```

? Version header enables upgrade tracking
? "When to Use" section documents activation context

#### Reference Contract: Spine ? Guides
```markdown
## Context-Specific Guides
- For [scenario], consult `.github/guides/[guide].md`
```

? Explicit reference pattern
? No implicit loading assumptions

### Security and Privacy

? No security implications - content reorganization only
? No new external dependencies
? No credential handling changes

### Scalability and Resilience

? Pattern supports future guides without spine changes
? Guide failures isolated (missing guide = missing feature, not workflow break)

### Dependency Analysis

| Dependency | Direction | Coupling |
|------------|-----------|----------|
| Spine ? Guides | Reference only | Loose |
| Guides ? Spine | None | Independent |
| Upgrade ? Guides | Download list | Must update |

### Implicit Assumptions Surfaced

1. **Assumption**: Copilot will load referenced files when relevant
   - **Risk**: May not work as expected
   - **Mitigation**: Test manually; spine still functional without guides

2. **Assumption**: Users upgrading will get guides directory created
   - **Risk**: Directory creation fails
   - **Mitigation**: Explicit `New-Item -Force` (per Reviewer)

3. **Assumption**: Version headers in guides stay synchronized with spine
   - **Risk**: Version drift
   - **Mitigation**: Single upgrade process updates all files atomically

### Failure Isolation

| Failure Scenario | Impact | Blast Radius |
|-----------------|--------|--------------|
| Guide file missing | Terminal/update instructions unavailable | Localized to feature |
| Guide file corrupted | Same as missing | Localized to feature |
| Spine missing guide reference | Users don't know to load guide | Workflow still works |

### Rollback Safety

? Single commit = single revert
? No database migrations
? No external service changes

---

## Architectural Concerns

### Concern 1: Version Synchronization (Accepted Risk)
**Issue**: Guide files have independent version headers. Could drift from spine.

**Decision**: Accept risk. Upgrade process updates all files atomically. Document that guide versions should match spine version.

**Impact**: No new User Story. Documentation note only.

---

## Summary

**Recommendation**: ? Approved for implementation

**Architectural notes to incorporate**:
1. Document that guide versions must match spine version
2. Ensure upgrade process is atomic (all-or-nothing)

No new User Stories required.
