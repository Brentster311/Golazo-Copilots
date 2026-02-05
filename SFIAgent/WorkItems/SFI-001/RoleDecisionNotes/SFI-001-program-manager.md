# SFI-001 Program Manager Decision Notes

## Date: 2026-02-03

### Design Decisions Made

#### 1. Project Structure
**Decision**: Use `src/` layout with `pyproject.toml`
**Rationale**: Modern Python best practice, enables proper packaging and distribution.

#### 2. Sync vs Async
**Decision**: Synchronous implementation for v1
**Rationale**: Simpler to implement and test. Async can be added later if performance demands it.

#### 3. Caching Strategy
**Decision**: JSON files in AppData directory
**Rationale**: Simple, human-readable, no additional dependencies. Can inspect cache manually for debugging.

#### 4. Discovery Approach
**Decision**: Probing + error analysis
**Rationale**: No known OpenAPI spec. Will need to probe endpoints and analyze responses to discover API surface.

#### 5. No CLI in v1
**Decision**: Library only
**Rationale**: Focus on solid foundation. CLI can be a separate module/story.

### Trade-offs Accepted

1. **Sync-only**: Limits concurrent operations but simplifies implementation
2. **File-based cache**: Not suitable for high-frequency access but adequate for developer tool
3. **AzureCliCredential only**: Requires az login; doesn't support service principals in v1

### Risks Flagged for Architect

1. Token caching strategy - azure-identity handles this but may need custom logic
2. API discovery may hit dead ends - need graceful failure handling
3. S360 API versioning is unknown - may need version detection

### Open Questions for QA

1. What constitutes "successful" API discovery? How many endpoints must be found?
2. Should cache corruption be automatically recovered, or raise error?
