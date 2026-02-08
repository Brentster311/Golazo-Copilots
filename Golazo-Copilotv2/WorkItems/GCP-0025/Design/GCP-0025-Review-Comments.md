# GCP-0025 Design Review Comments

## Summary

The design is **approved with minor recommendations**. The approach to replace DoR/DoD marking with role-based output validation is sound and addresses the core friction issues.

## Clarity and Completeness

### ✓ Strengths
- Clear problem statement and business case
- Well-defined validation types (file, dir, git-branch, git-log)
- Phased approach reduces risk
- Rollback plan exists

### ⚠ Recommendations

1. **R1: Clarify git-log validation**
   - Current: `git-log: <pattern>` 
   - Question: Does pattern match commit message? Branch name? Both?
   - Recommendation: Use `git log --oneline --all --grep=<pattern> | head -1` and check non-empty

2. **R2: Handle missing role files gracefully**
   - What happens if a role file is missing or malformed?
   - Recommendation: Log warning, allow transition (fail open for missing role file)

3. **R3: Define validation error format**
   - Standardize error response structure for missing outputs
   - Include: item type, expected path, actual check performed

## Feasibility and Sequencing

### ✓ Phasing is appropriate
- Phase 1 can be developed with full test coverage before integration
- Phase 3 (removal) is clean after new system proven

### ⚠ Recommendation

4. **R4: Add Phase 0 - Deprecation warnings**
   - Before removing gcp_mark_dor/dod, have them emit deprecation warnings
   - This helps users of older instructions migrate

## Risk Coverage

### ✓ Risks identified
- Role file parsing errors
- Git commands fail  
- Breaking existing workflows

### ⚠ Additional risks

5. **R5: Add risk - Circular dependency**
   - If role file A requires output from role B, and B requires A
   - Mitigation: Validate only current role's outputs, not future roles

6. **R6: Add risk - Performance with many outputs**
   - Git commands can be slow on large repos
   - Mitigation: Limit to 10 outputs per role, parallelize git calls

## Edge Cases

7. **R7: Empty Required Outputs section**
   - If a role has `## Required Outputs` with no items, treat as "no requirements"
   
8. **R8: Role notes special handling**
   - Role notes are currently checked separately in gcp_transition
   - Decision: Keep role notes as separate check, OR move to Required Outputs?
   - **Resolution**: Keep as separate check. Role notes document decisions; Required Outputs are work artifacts.

## Naming Clarity

### ✓ Good
- `output_validator.py` - clear purpose
- `{id}` placeholder - simple and intuitive

### ⚠ Recommendation

9. **R9: Rename git-log to git-commit-msg**
   - `git-log: <pattern>` implies searching log
   - `git-commit-msg: <pattern>` clearer that we're matching commit messages

## Approval Status

| Reviewer | Status | Notes |
|----------|--------|-------|
| QA | **Approved** | Address R1, R8 before implementation |

---

## Architect Notes

### Architectural Alignment

✓ **Approved** - Design aligns with existing Golazo architecture:
- MCP server pattern maintained
- Role files remain source of truth
- State.json simplified (dor/dod removed)

### API and Data Contracts

#### Modified Tools

| Tool | Change | Contract Impact |
|------|--------|-----------------|
| `gcp_transition` | Add output validation | New error response when outputs missing |
| `gcp_status` | Add outputs section | New `required_outputs` field in response |

#### Removed Tools

| Tool | Replacement |
|------|-------------|
| `gcp_mark_dor` | Automatic validation on transition |
| `gcp_mark_dod` | Automatic validation on transition |

#### New Module: `output_validator.py`

```python
@dataclass
class OutputSpec:
    type: str  # "file", "dir", "git-branch", "git-log"
    path_or_pattern: str

@dataclass  
class ValidationResult:
    valid: bool
    message: str
    outputs: list[dict]  # Each with {spec, valid, message}

def parse_required_outputs(role_content: str, work_item_id: str) -> list[OutputSpec]
def validate_outputs(specs: list[OutputSpec], workspace_path: Path) -> ValidationResult
```

### Security and Privacy

✓ No security concerns - local file system access only, no credentials or secrets involved.

### Scalability and Resilience

| Concern | Assessment |
|---------|------------|
| Many outputs per role | Low risk - recommend max 10, warn if exceeded |
| Git commands slow | Low risk - timeout already exists (5s), add caching per call |
| Role file parsing | Low risk - simple regex, fails gracefully |

### Dependency Choices

✓ No new dependencies required.

### Failure Isolation

| Failure Mode | Handling |
|--------------|----------|
| Role file missing | Warn, allow transition (fail open) |
| Role file malformed | Warn, allow transition (fail open) |
| Git not available | Skip git validations with warning |
| Output validation timeout | Fail with clear error, suggest force |

### Implicit Assumptions Surfaced

1. **Path separator**: Use `Path` for cross-platform support
2. **Git encoding**: Specify `encoding="utf-8"` for git commands
3. **Pattern matching**: Use shell glob for git-branch (`*` wildcard)

### Architect Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Fail open on missing role file | Yes | Don't block work due to meta-issue |
| Cache validation per call | Yes | Same outputs checked once per transition |
| Max outputs per role | 10 (soft limit, warn) | Prevent performance issues |

### No New User Stories Required

Design is complete as specified. No architectural changes needed.
