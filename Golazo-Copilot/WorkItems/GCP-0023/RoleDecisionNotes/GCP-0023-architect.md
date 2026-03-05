# GCP-0023 Architect Notes

## Architectural Review Summary

### Verdict: ✅ APPROVED

The design is architecturally sound and follows existing patterns.

## Key Decisions

### 1. Module Placement
**Decision:** New `evidence.py` in `src/golazo_copilot/core/`
**Rationale:** Core validation logic, reusable across tools

### 2. State Schema Version
**Decision:** Bump to `1.1` with backward-compatible structure
**Rationale:** 
- Old readers ignore unknown fields
- New readers handle both formats
- No migration required

### 3. EvidenceResult Dataclass
**Decision:** Use dataclass instead of tuple
**Rationale:**
- Named fields improve readability
- Extensible for future fields
- Type-safe

### 4. Git Command Execution
**Decision:** Use `subprocess.run()` with explicit encoding
**Rationale:**
- Avoid encoding issues on Windows
- Capture stderr for error messages
- Timeout protection (5s max)

## Contracts Defined

### Evidence Types
| DoR/DoD Item | Evidence Type | Validation |
|--------------|---------------|------------|
| userStory, designDoc, reviewComments, testCases | `str` (file path) | File exists |
| branchCreated | `str` (branch name) | `git branch --list` |
| committed | `str` (SHA) | `git rev-parse --verify` |
| testsWrittenFirst, docsUpdated | `str \| list[str]` | All files exist |
| testsPass, buildPasses | `str` (output/link) | Non-empty string |
| refactorComplete | `str` (path or "N/A: reason") | Path exists OR starts with "N/A:" |

### Error Format
```
[FAIL] Invalid evidence for '<item>': <reason>
Expected: <format description>
Example: <concrete example>
```

## Security Notes
- No secrets should appear in evidence strings
- File paths may contain usernames (e.g., `/Users/brent/...`) - sanitize in logs if needed
- Git SHAs are public information

## No New User Stories Required
All recommendations fit within current scope.

## Ready for Developer
Architecture approved. DoR complete. Ready to transition to development phase.
