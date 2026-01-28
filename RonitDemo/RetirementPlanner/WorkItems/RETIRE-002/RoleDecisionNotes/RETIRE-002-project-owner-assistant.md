# Project Owner Assistant Decision Notes: RETIRE-002

## Work Item
RETIRE-002 - Encrypt User Financial Data at Rest

## Origin
This story was created based on:
1. **User explicit request**: "Encryption of data at rest is for sure a required story"
2. **Architect feedback** in RETIRE-001 Review Comments: "Encryption could be RETIRE-00X"

## Decisions Made

### 1. Separate Story vs. Adding to RETIRE-001
**Decision**: Create separate story RETIRE-002.

**Rationale**:
- Golazo rule: Reviewer/Architect feedback that changes scope becomes new User Story
- Encryption is a distinct security feature, not part of MVP core functionality
- RETIRE-001 can be completed and tested independently
- Allows user to prioritize encryption timing

### 2. Dependency on RETIRE-001
**Decision**: RETIRE-002 depends on RETIRE-001.

**Rationale**:
- Repository abstraction in RETIRE-001 enables clean encryption implementation
- Encryption wraps or extends existing repository
- No value encrypting data if base app doesn't exist

### 3. Key Management Approach
**Decision**: App-managed key, no user password for MVP.

**Rationale**:
- User said "for now" it's just for them (technical user)
- Password-based encryption adds UX complexity
- Can be enhanced in future story if needed
- OS-level protection (user profile folder) provides base security

### 4. Migration Path
**Decision**: Auto-migrate unencrypted data on first run.

**Rationale**:
- User shouldn't lose existing data when upgrading
- One-time migration is simple
- Document that rollback loses encrypted data

### 5. Scope Boundaries
**Decision**: Encrypt entire JSON blob, not field-level.

**Rationale**:
- Simpler implementation
- All data is equally sensitive (financial)
- Field-level encryption is overkill for single-user local app

## Alternatives Considered

### Alternative: Add encryption to RETIRE-001
**Rejected**: Violates Golazo rule about scope changes. Also increases RETIRE-001 complexity and delays MVP.

### Alternative: Password-based encryption
**Deferred**: Adds UX complexity. Can be future story if user wants it.

### Alternative: Field-level encryption
**Rejected**: Overkill. No use case for partial encryption in this context.

## Tradeoffs Accepted
- **App-managed key over password**: Less secure but simpler UX
- **Whole-file encryption over field-level**: Less flexible but simpler implementation
- **Single algorithm over configurable**: Less future-proof but MVP-appropriate

## Known Limitations
- If encryption key is lost, data cannot be recovered
- No key backup/recovery mechanism in MVP
- Rollback to pre-encryption version loses data

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Key storage location varies by OS | Medium | Document/test on Windows (primary platform) |
| Cryptography library compatibility | Low | Use well-established library (cryptography or Fernet) |
| Migration fails on corrupt file | Low | Handle gracefully, allow fresh start |

## Related Stories (Future)
- RETIRE-00X: Password-protected app access
- RETIRE-00X: Key backup/recovery
- RETIRE-00X: Key rotation
