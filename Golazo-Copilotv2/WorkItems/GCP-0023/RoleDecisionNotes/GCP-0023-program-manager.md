# GCP-0023 Program Manager Notes

## Design Decisions

### 1. Evidence Schema Design
**Decision:** Nested object structure for DoR/DoD items
```json
{
  "dor": {
    "userStory": { "complete": true, "evidence": "path/to/file.md", "validated_at": "2026-02-07T..." }
  }
}
```
**Rationale:** Allows storing metadata (validation timestamp) alongside evidence, extensible for future fields (validator version, etc.)

### 2. Validation Strictness
**Decision:** File-based evidence requires file existence; command-based evidence is accepted as-is
**Rationale:** 
- We can't re-run tests/builds (expensive, stateful)
- File checks are cheap and deterministic
- Git operations are local and fast

### 3. Backward Compatibility Strategy
**Decision:** Dual-mode parsing - old boolean format continues to work
**Rationale:** 
- Avoids breaking existing work items
- Gradual migration path
- No forced mass update

### 4. Evidence Path Format
**Decision:** Accept both relative (to workspace) and absolute paths; store as provided
**Rationale:** 
- Flexibility for different invocation contexts
- Let user decide their preference
- Validation resolves paths internally

### 5. N/A Handling for refactorComplete
**Decision:** Accept "N/A: <reason>" as valid evidence
**Rationale:** 
- Not all work items need refactoring
- Requires explicit justification
- Auditable decision

## Phased Implementation
1. **Schema Update** - Foundation, no behavior change
2. **Validation Functions** - Core logic, testable in isolation
3. **Mark Tool Updates** - Integration, user-facing change
4. **Test Updates** - Ensure coverage

## Risk Acknowledgments
- Test update burden is real; will create helper fixture
- Git availability assumption is reasonable for dev workflows
- Error message quality is critical for adoption

## Ready for QA/Architect Review
Design doc captures requirements, approach, and trade-offs. Ready for critique.
