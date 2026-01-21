# Program Manager Decision Notes: MCDEMO-001

## Date: Retrospective Documentation
## Role: Program Manager

---

## Decisions Made

### 1. Design Document Structure
**Decision**: Created comprehensive design document with business case, architecture diagram, and test strategy.
**Rationale**: Follows Golazo template requirements and provides complete context for reviewers.

### 2. Component Architecture
**Decision**: Three-layer architecture (Models ? Cache ? Adapter)
**Rationale**: Clean separation of concerns, testable in isolation, follows SOLID principles.

### 3. Authentication Approach
**Decision**: Use AzureCliCredential from azure-identity
**Rationale**: Most user-friendly for local development; users familiar with `az login`.

### 4. Caching Strategy
**Decision**: JSON file-based cache in user's home directory
**Rationale**: Simple, portable, no additional dependencies; suitable for MVP.

## Alternatives Considered

| Option | Considered | Reason Not Chosen |
|--------|------------|-------------------|
| Direct Kusto SDK | Yes | accia-datacollection provides simpler interface |
| SQLite cache | Yes | JSON is simpler for this use case |
| Token-based auth | Yes | CLI credential is more user-friendly |

## Tradeoffs Accepted

1. **Simplicity over features**: No cache TTL configuration (acceptable for MVP)
2. **Local-first**: No cloud sync of cached schemas (can be added later)

## Known Limitations

1. Requires user to run `az login` before use
2. Cache invalidation is manual
3. No GUI implementation in this story (deferred)

## Risks

| Risk | Mitigation |
|------|------------|
| Auth complexity | Clear error messages with guidance |
| Network failures | Caching reduces repeated queries |

## Outcome
Design document created and ready for review.
