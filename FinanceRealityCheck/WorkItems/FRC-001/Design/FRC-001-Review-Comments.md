# FRC-001 Review Comments

## Domain Expert Guidance
### Experts consulted
- Financial data integration domain expert
- Security and privacy domain expert

### Recommendations
- Introduce connector abstraction with provider-specific adapters and per-account isolation.
- Normalize provider payloads to canonical schema prior to persistence.
- Enforce idempotent ingestion via provider/account-scoped transaction identifiers.
- Encrypt sensitive financial payloads and avoid plaintext token storage.
- Add structured sync result reporting with actionable error categories and retry guidance.

### Risks and constraints
- Institution-specific API/OFX variability can cause partial sync failures.
- Local key management quality determines actual security posture.
- Mis-normalized merchants will degrade categorization learning quality.

### Suggested design clarifications
- Define canonical error categories for sync failures.
- Define key bootstrap and rotation guidance for local environments.
- Define dedupe contract explicitly in implementation and tests.

## Quality Assurance Review
### Design clarity and completeness
- The design is coherent for a first vertical slice and maps to all current acceptance criteria.
- API/service contracts should explicitly document payload schemas for link, sync, categorize, and budget endpoints to reduce implementation ambiguity.

### Feasibility and sequencing
- Backend-first sequencing is feasible and lowers risk before UI polish.
- The team should implement connector abstraction and storage primitives before introducing categorization learning to avoid rework.

### Edge cases and failure modes to test
- Partial provider outage where one institution succeeds and one fails in the same sync run.
- Repeated sync of same interval must not create duplicates.
- Invalid category updates and missing budget categories must return actionable validation errors.
- Corrupt encryption key or unreadable encrypted payload should fail gracefully with retry guidance.

### Testability assessment
- All acceptance criteria are testable via integration and unit tests.
- Add explicit assertions for encrypted-at-rest behavior and dedupe integrity.

### Recommendation to Developer
- Implement deterministic transaction identity and explicit error categories first.
- Ensure test cases are implemented before production code in strict TDD order.

## Architect Notes
### Architectural boundaries
- Preserve clear separation: connector adapters (provider specifics), normalization pipeline (canonical model), repository (encrypted persistence), and planning services (categorization + budgets).
- Keep API layer thin so core rules remain testable without HTTP transport.

### Contracts and failure handling
- Define explicit request/response contracts for:
	- Account link
	- Sync run result (per-account success/failure, imported count, duplicates skipped)
	- Category confirmation/update
	- Budget upsert and overspend alerts
- Enforce stable error taxonomy: auth_error, connectivity_error, provider_schema_error, validation_error, storage_error.

### Security and privacy
- Encrypt transaction payloads and provider tokens before persistence.
- Avoid logging secrets or plaintext sensitive payloads.
- Keep local encryption key out of repository and provide deterministic first-run bootstrap behavior.

### Scalability and resilience
- Use idempotent upsert with unique provider/account transaction identity.
- Isolate per-account sync failures so one provider/account does not fail the full sync run.

### Default-behavior checks
- Validate default sqlite transaction behavior is atomic for multi-record sync batches.
- Validate datetime parsing defaults (timezone and naive date handling) to avoid off-by-one day ranges in 90-day sync windows.

### Capability registry impact
- Impact analysis run for design artifacts; currently zero affected capabilities in registry.
