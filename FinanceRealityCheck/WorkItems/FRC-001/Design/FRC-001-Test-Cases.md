# FRC-001 Test Cases

## Test Strategy
This suite follows TDD-first principles and maps each acceptance criterion to at least one concrete test with explicit expected outcomes and failure messages.

## Acceptance Criteria Coverage Matrix

### AC1: Link First Tech + Fidelity and import 90-day transactions
- TC-AC1-001 (Integration): Link one First Tech and one Fidelity account, run sync for 90 days.
  - Expected outcome: Sync result indicates success for both accounts and imported count > 0 for each.
  - Failure message: "Expected successful 90-day sync for both institutions, but one or more accounts failed or imported zero transactions."

### AC2: Normalize schema and store encrypted locally
- TC-AC2-001 (Unit/Integration): Verify normalized fields exist for each imported record: date, amount, merchant, account, direction.
  - Expected outcome: All persisted records deserialize to canonical schema with required fields populated.
  - Failure message: "Transaction schema normalization failed: required field missing or invalid."
- TC-AC2-002 (Integration): Verify encrypted-at-rest behavior.
  - Expected outcome: Raw persistence payload does not expose plaintext merchant/description.
  - Failure message: "Encryption-at-rest check failed: sensitive transaction text found in raw storage payload."

### AC3: Assisted categorization with reusable confirmed edits
- TC-AC3-001 (Integration): Confirm/edit category for a merchant, re-sync transaction from same merchant.
  - Expected outcome: Subsequent transaction from same normalized merchant is auto-proposed with learned category.
  - Failure message: "Categorization learning failed: confirmed user category was not reused on subsequent matching transaction."

### AC4: Monthly category-cap budgets and overspend warning
- TC-AC4-001 (Integration): Create at least five category caps, ingest debit transactions exceeding one cap.
  - Expected outcome: Overspend warning emitted for exceeded category and month context included.
  - Failure message: "Budget alert generation failed: exceeded category cap did not produce warning."

### AC5: Actionable errors and retry without corruption
- TC-AC5-001 (Integration): Force one account sync failure while another succeeds.
  - Expected outcome: Failed account returns actionable error category/message; successful account data persists.
  - Failure message: "Expected actionable per-account sync error with partial-success handling, but result was missing/ambiguous."
- TC-AC5-002 (Integration): Retry after failure.
  - Expected outcome: Retry succeeds when failure condition is cleared and no duplicate transactions are created.
  - Failure message: "Retry safety failed: retry did not recover or duplicate records were introduced."

## Additional Quality Tests
- TC-Q-001 (Unit): Duplicate prevention enforces unique provider/account transaction identity.
- TC-Q-002 (Unit): Invalid budget cap input (negative cap) returns validation error.
- TC-Q-003 (Unit): Invalid category confirmation input returns validation error.
- TC-Q-004 (Unit): Current-month budget computation excludes credits from spend totals.

## Performance-Sensitive Test
- TC-P-001 (Integration): Budget and category views remain responsive with 10,000 transactions.
  - Expected outcome: Aggregation path executes without timeout under local test constraints.
  - Failure message: "Performance guard failed: budget aggregation exceeded acceptable runtime for 10,000 transactions."

## Security-Focused Test
- TC-S-001 (Unit): Provider tokens and transaction payloads are encrypted before persistence.
  - Expected outcome: Raw stored values are ciphertext and decrypt correctly only with active local key.
  - Failure message: "Security guard failed: sensitive fields persisted without encryption or decryption integrity failed."
