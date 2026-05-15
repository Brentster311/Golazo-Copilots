# FRC-001 Domain Expert Notes

## Domain Analysis
This work item requires domain guidance in two areas:

1. Financial data integration domain
- Reason: Institution connectivity and transaction normalization reliability are core acceptance criteria.

2. Security and privacy domain
- Reason: Local encrypted storage and sensitive financial data handling are core non-functional requirements.

## Consulted Domain Perspectives
### Financial Integration Expert Guidance
- Use a connector abstraction boundary with provider-specific adapters so provider failures do not corrupt core ingestion flow.
- Normalize all provider payloads to a canonical transaction schema before persistence.
- Treat source transaction identifiers as provider/account scoped identifiers to guarantee deterministic deduplication.
- Capture sync outcomes per institution/account with actionable failure classification (auth, connectivity, parsing, data shape).

### Security Expert Guidance
- Encrypt sensitive transaction payloads at rest with application-level encryption.
- Do not persist provider credentials/tokens in plaintext.
- Keep local key material outside version-controlled artifacts.
- Return user-safe, non-secret-bearing error messages.

## Risks and Constraints Identified
- Provider schema and availability variance can reduce sync reliability.
- Weak key handling practices can invalidate local-only security claims.
- Categorization quality depends on correctness of merchant normalization.

## Suggested Design Modifications
- Add a sync run result model with per-account status and retry-safe semantics.
- Add deterministic idempotency guardrails for transaction ingestion.
- Add explicit key management bootstrap behavior for first-run local setup.

## Outcome
Domain expertise is required and has been documented in Review Comments for downstream QA and Architect review.
