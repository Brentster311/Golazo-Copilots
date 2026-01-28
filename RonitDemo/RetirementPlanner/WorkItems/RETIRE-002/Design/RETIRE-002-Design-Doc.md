# Design Document: RETIRE-002

## Summary
Add encryption at rest to the retirement planner application, ensuring user financial data is encrypted when stored on disk and decrypted transparently when loaded.

## Problem Statement
User financial data (savings, income goals, contributions) stored in plaintext JSON can be read by anyone with file system access. This creates a privacy risk if the user's computer is compromised, shared, or accessed by others.

## Business Case

### Why Now
- Architect identified plaintext storage as a security consideration in RETIRE-001 review
- User explicitly confirmed encryption is a required feature
- Best implemented early before users accumulate sensitive data

### Impact
- Protects user's financial privacy
- Builds trust in the application
- Enables future multi-user or cloud scenarios

### KPIs
- Encrypted file cannot be read without app
- Zero user-facing changes to workflow
- Migration from unencrypted data succeeds

## Stakeholders
| Role | Name/Description | Interest |
|------|------------------|----------|
| User | Project Owner | Wants data protected |
| Developer | Copilot-assisted | Implementation |

## Functional Requirements
| ID | Requirement | Source |
|----|-------------|--------|
| FR-1 | Encrypt user profile data before writing to disk | AC-1 |
| FR-2 | Decrypt user profile data when loading from disk | AC-2 |
| FR-3 | Encrypted file must not contain readable plaintext | AC-3 |
| FR-4 | Encryption/decryption transparent to user | AC-4 |
| FR-5 | Handle missing/corrupted key gracefully | AC-5 |
| FR-6 | Migrate existing unencrypted data automatically | AC-6 |

## Non-Functional Requirements
| ID | Requirement | Metric |
|----|-------------|--------|
| NFR-1 | Performance impact imperceptible | < 100ms added latency |
| NFR-2 | Use vetted cryptography library | cryptography/Fernet |
| NFR-3 | Platform-appropriate key storage | Windows: %APPDATA% |

## Proposed Approach

### Architecture Overview
```
???????????????????????????????????????????????????????????
?                    Presentation Layer                    ?
?                  (Tkinter GUI - unchanged)               ?
???????????????????????????????????????????????????????????
?                    Business Logic Layer                  ?
?            (RetirementCalculator - unchanged)            ?
???????????????????????????????????????????????????????????
?                   Data Access Layer                      ?
?     ???????????????????????????????????????????????     ?
?     ?         IDataRepository (Interface)          ?     ?
?     ???????????????????????????????????????????????     ?
?                          ?                               ?
?     ???????????????????????????????????????????????     ?
?     ?   EncryptedJsonFileRepository (NEW)          ?     ?
?     ?   - wraps/replaces JsonFileRepository        ?     ?
?     ?   - encrypts on save, decrypts on load       ?     ?
?     ???????????????????????????????????????????????     ?
?                          ?                               ?
?     ???????????????????????????????????????????????     ?
?     ?         EncryptionService (NEW)              ?     ?
?     ?   - key generation/storage                   ?     ?
?     ?   - encrypt/decrypt operations               ?     ?
?     ???????????????????????????????????????????????     ?
???????????????????????????????????????????????????????????
```

### Technology Stack Addition
| Component | Technology | Rationale |
|-----------|------------|-----------|
| Encryption Library | `cryptography` (Fernet) | Well-vetted, simple API, AES-128-CBC |
| Key Storage | OS app data folder | Platform-appropriate, user-isolated |

### Component Breakdown

#### 1. EncryptionService (`services/encryption_service.py`)
```python
class EncryptionService:
    def __init__(self, key_path: Path):
        """Initialize with path to key file."""
        
    def get_or_create_key(self) -> bytes:
        """Load existing key or generate new one."""
        
    def encrypt(self, plaintext: str) -> bytes:
        """Encrypt string data using Fernet."""
        
    def decrypt(self, ciphertext: bytes) -> str:
        """Decrypt data back to string."""
```

#### 2. EncryptedJsonFileRepository (`repository/encrypted_json_file_repository.py`)
```python
class EncryptedJsonFileRepository(IDataRepository):
    def __init__(self, file_path: Path, encryption_service: EncryptionService):
        """Initialize with file path and encryption service."""
        
    def save(self, profile: UserProfile) -> None:
        """Serialize to JSON, encrypt, write to file."""
        
    def load(self) -> UserProfile | None:
        """Read file, decrypt, deserialize from JSON."""
        
    def migrate_if_needed(self) -> None:
        """Check for unencrypted file and migrate."""
```

### Encryption Details

#### Algorithm
- **Fernet** (from `cryptography` library)
- Uses AES-128-CBC with HMAC for authentication
- Handles IV generation automatically
- Simple, hard to misuse

#### Key Management
```
Key Location (Windows): %APPDATA%\RetirementPlanner\encryption.key
Key Location (Linux):   ~/.config/RetirementPlanner/encryption.key
Key Location (Mac):     ~/Library/Application Support/RetirementPlanner/encryption.key
```

#### Key Generation
- First run: Generate 32-byte random key using `Fernet.generate_key()`
- Store in app data folder (not with data file)
- Load key on subsequent runs

### Migration Strategy

```
On application start:
1. Check if encrypted file exists ? load encrypted
2. Check if unencrypted file exists ? migrate:
   a. Load unencrypted JSON
   b. Encrypt and save to new file
   c. Rename old file to .backup
3. Neither exists ? fresh start
```

### File Structure Changes
```
RetirementPlanner/
??? src/
?   ??? services/
?   ?   ??? encryption_service.py  # NEW
?   ?   ??? retirement_calculator.py
?   ??? repository/
?       ??? encrypted_json_file_repository.py  # NEW
?       ??? json_file_repository.py
??? data/
?   ??? user_profile.enc  # encrypted file (changed extension)
??? tests/
    ??? test_encryption_service.py  # NEW
    ??? test_encrypted_repository.py  # NEW
```

## Alternatives Considered

### Alternative: Use `cryptography` vs standard library
| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| `cryptography` (Fernet) | Simple, secure, hard to misuse | External dependency | **Selected** |
| `hashlib` + `os.urandom` | No dependency | Easy to implement wrong | Rejected |
| `pycryptodome` | Powerful | Complex API, overkill | Rejected |

### Alternative: Decorator pattern vs new repository
| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| New repository class | Simple, clear | Some code duplication | **Selected** |
| Decorator wrapping existing | DRY, composable | More complex | Future option |

## Risks and Mitigations
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Key loss = data loss | Low | High | Document clearly, consider backup story |
| Migration corrupts data | Low | Medium | Keep .backup of original file |
| Dependency issues | Low | Medium | Pin `cryptography` version |

## Open Questions
1. ~~Should we add password protection?~~ **Decision**: No, deferred to future story.
2. ~~Key backup mechanism?~~ **Decision**: Out of scope, future story.

## Dependencies
- `cryptography` library (new external dependency)
- RETIRE-001 completed (repository interface exists)

## Migration / Rollout / Rollback Plan
- **Rollout**: Update app, auto-migrates on first run
- **Rollback risk**: Downgrade loses access to encrypted data
- **Mitigation**: Keep .backup of original unencrypted file

## Test Strategy Summary
| Test Type | Scope | Tools |
|-----------|-------|-------|
| Unit Tests | EncryptionService | pytest |
| Unit Tests | EncryptedJsonFileRepository | pytest |
| Integration | Migration from unencrypted | pytest |
| Manual | Verify file is not readable | Hex editor |
