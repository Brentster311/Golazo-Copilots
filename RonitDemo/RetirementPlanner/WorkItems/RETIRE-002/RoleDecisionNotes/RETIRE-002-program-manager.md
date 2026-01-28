# Program Manager Decision Notes: RETIRE-002

## Work Item
RETIRE-002 - Encrypt User Financial Data at Rest

## Decisions Made

### 1. Encryption Library: cryptography (Fernet)
**Decision**: Use the `cryptography` library with Fernet encryption.

**Rationale**:
- Fernet is specifically designed to be hard to misuse
- Handles IV generation, padding, and HMAC automatically
- Well-audited, widely used library
- Simple API reduces implementation errors

**Tradeoff**: First external dependency, but security justifies it.

### 2. Key Storage Location
**Decision**: Store encryption key in OS-specific app data folder.

| OS | Location |
|----|----------|
| Windows | `%APPDATA%\RetirementPlanner\encryption.key` |
| Linux | `~/.config/RetirementPlanner/encryption.key` |
| Mac | `~/Library/Application Support/RetirementPlanner/encryption.key` |

**Rationale**:
- Separates key from encrypted data
- OS provides user isolation
- Standard location for app config/secrets

### 3. Migration Approach
**Decision**: Auto-migrate with backup preservation.

**Flow**:
1. Detect unencrypted file
2. Load and encrypt
3. Save to new `.enc` file
4. Rename original to `.backup`

**Rationale**:
- Seamless user experience
- Preserves original as safety net
- One-time operation

### 4. New Repository vs. Decorator
**Decision**: Create new `EncryptedJsonFileRepository` class.

**Rationale**:
- Simpler to understand and test
- Clear separation of concerns
- Repository pattern already supports swapping implementations
- Decorator could be refactored later if needed

### 5. File Extension Change
**Decision**: Change from `.json` to `.enc` for encrypted files.

**Rationale**:
- Signals that file is not plain JSON
- Prevents accidental editing
- Easy to identify encrypted vs unencrypted

## Alternatives Considered

### Alternative: Password-based key derivation
**Deferred**: Would require password prompt on every launch. User said MVP is just for them. Future story.

### Alternative: Windows DPAPI for key protection
**Deferred**: Windows-specific. Would complicate cross-platform if ever needed. Simple file storage is acceptable for MVP.

### Alternative: Encrypt individual fields
**Rejected**: All fields are equally sensitive. Whole-file encryption is simpler and equally secure.

## Tradeoffs Accepted
1. **External dependency**: `cryptography` added for security correctness
2. **Key in file**: Less secure than OS keychain, but simpler
3. **No key backup**: Data loss risk if key lost, but MVP simplicity

## Known Limitations
1. Key stored as file (could be read by other apps with user permissions)
2. No key backup/recovery mechanism
3. Downgrade path loses data access
4. Single key for all data (no per-field keys)

## Risks

| Risk | Mitigation |
|------|------------|
| Key file deleted | Document location, suggest backup |
| Migration fails | Keep .backup file |
| Library vulnerability | Pin version, monitor advisories |

## Impact on RETIRE-001
- **No changes to RETIRE-001 scope**
- RETIRE-002 uses repository interface from RETIRE-001
- `main.py` will need to inject `EncryptedJsonFileRepository` instead of `JsonFileRepository`

## Open Items for Reviewer/Architect
1. Confirm Fernet is acceptable encryption choice
2. Review key storage location decision
3. Validate migration approach
