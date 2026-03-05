# GCP-0023 Design Review Comments

## Overall Assessment
**Status:** ✅ APPROVED with minor recommendations

The design is well-structured, addresses backward compatibility, and has a clear phased implementation plan.

---

## Clarity and Completeness

### ✅ Strengths
- Clear evidence type mapping table
- Explicit validation rules per item type
- Schema change is well-defined

### ⚠️ Recommendations
1. **Clarify path resolution**: Design says "relative to workspace root" but doesn't specify how workspace root is determined when `workspace_path` isn't provided
   - **Suggestion:** Document that relative paths are resolved against the `work_items_dir` parent

2. **Define "evidence" parameter type**: Is it always a string, or can it be a list for `testsWrittenFirst` / `docsUpdated`?
   - **Suggestion:** Accept `str | list[str]` for items that may have multiple files

---

## Feasibility and Sequencing

### ✅ Strengths
- Phased approach allows incremental delivery
- Each phase is independently testable

### ⚠️ Recommendations
1. **Phase 2 before Phase 1?** Validation functions don't depend on schema change
   - **Suggestion:** Could parallelize Phase 1 and 2

---

## Risk Coverage

### ✅ Strengths
- Git availability risk acknowledged
- Backward compatibility addressed

### ⚠️ Missing Risks
1. **Windows path separators**: Git commands may behave differently with backslashes
   - **Mitigation:** Normalize paths to forward slashes before git operations

2. **Git not in PATH**: `subprocess` will fail silently
   - **Mitigation:** Check for git availability at startup, warn if missing

---

## Edge Cases and Failure Modes

### Cases to Test
1. Evidence path with spaces
2. Evidence path with unicode characters
3. Evidence path that exists but is a directory (not file)
4. Git SHA that's valid format but doesn't exist
5. Branch name with special characters
6. Empty string as evidence
7. Very long evidence strings (>1000 chars)

---

## Naming Clarity

### ✅ Good
- `evidence.py` is clear
- `validate_*` function names are descriptive

---

## Architect Notes

### Architectural Alignment
**Status:** ✅ APPROVED

The design fits cleanly within the existing MCP tool architecture:
- New `evidence.py` module in `core/` follows existing patterns
- Mark tools already accept `work_items_dir`, adding `evidence` is consistent
- State schema evolution is backward-compatible

### API Contracts

#### Evidence Parameter Contract
```python
evidence: str | list[str]  # Required for mark operations
```

#### Validation Result Contract
```python
@dataclass
class EvidenceResult:
    valid: bool
    message: str  # Error message if invalid, empty if valid
    normalized_path: str | None  # Resolved path if applicable
```

#### State Schema Contract (v1.1)
```json
{
  "schema_version": "1.1",
  "dor": {
    "userStory": {
      "complete": true,
      "evidence": "WorkItems/GCP-0023/GCP-0023-User-Story.md",
      "validated_at": "2026-02-07T12:00:00Z"
    }
  }
}
```

### Security & Privacy
- ✅ No secrets in evidence (file paths, git refs, command output)
- ✅ Evidence stored locally only (no network transmission)
- ⚠️ **Recommendation:** Sanitize evidence strings before logging (remove potential PII in filenames)

### Failure Isolation
- Validation failure is isolated to the mark operation
- No cascading failures to other tools
- State remains consistent on validation failure (not updated)

### Dependency Analysis
- `subprocess` for git commands (stdlib, no new deps)
- `pathlib` for file operations (stdlib)
- `datetime` for timestamps (stdlib)
- **No new external dependencies**

### Implicit Behaviors Surfaced

1. **`Path.exists()` follows symlinks** - Is this desired?
   - **Decision:** Yes, symlinks are valid references

2. **`subprocess.run()` default encoding** - Could cause issues on non-UTF8 systems
   - **Decision:** Explicitly set `encoding='utf-8'` in git calls

3. **`git rev-parse` accepts partial SHAs** - Is this desired?
   - **Decision:** Yes, standard git behavior (7+ chars)

### Rollback Safety
- Schema v1.1 is backward-compatible with v1.0 readers
- Old tools ignore new `evidence` fields
- Rollback to v2.14.x continues to function

### ⚠️ Suggestion
- Consider `EvidenceResult` as a named tuple/dataclass instead of `tuple[bool, str]`

---

## Operational Impact

### On-Call
- No new on-call burden (local validation only)

### Failure Modes
- Validation failure is user-recoverable
- No data loss scenarios

---

## Summary of Recommendations

| # | Recommendation | Priority |
|---|----------------|----------|
| 1 | Clarify path resolution documentation | Medium |
| 2 | Support list of paths for multi-file evidence | High |
| 3 | Normalize paths for Windows compatibility | High |
| 4 | Check git availability at startup | Low |
| 5 | Use EvidenceResult dataclass | Low |

**Verdict:** Proceed to implementation with recommendations incorporated.
