# FRC-001 Design Doc

## Summary
Deliver the first executable slice of the personal financial planner: connect First Tech Federal Credit Union and Fidelity accounts, ingest 90-day transactions into an encrypted local store, support assisted categorization with learning from user corrections, and provide category-cap budget overspend warnings.

## Problem Statement
Today financial data and planning actions are fragmented across institutions and manual workflows. This creates delayed visibility into spending patterns, weak budget adherence, and low confidence in planning decisions. The first slice must establish dependable account ingestion and baseline planning workflows before advanced intelligence is layered on.

## Business Case (Why Now, Impact, KPIs)
Why now:
- Data acquisition reliability is the critical path for all downstream planning features.
- Early warning on budget drift provides immediate behavioral value.

Expected impact:
- Single pane of data from initial institutions.
- Faster categorization and improved budget awareness.

Initial KPIs:
- Sync success rate by institution >= 95% for normal (non-expired) credentials.
- Duplicate prevention rate = 100% for repeated sync of same date range.
- User correction ratio decreases week-over-week as learned rules accumulate.
- Overspend alerts generated before month end for overspent categories.

## Stakeholders
- Primary user: Brent (single-user personal planner)
- Future stakeholder: POA workflow consumers for follow-on slices

## Functional Requirements
1. Account linking
- User can link at least one First Tech account and one Fidelity account.
- Linked accounts are persisted locally.

2. Transaction sync
- User can trigger sync for linked accounts for the last 90 days.
- Transactions are normalized to: date, amount, merchant/description, account, direction.
- Re-sync is idempotent; duplicate records are prevented.

3. Encrypted local storage
- Transaction payloads are stored encrypted at rest in local persistence.

4. Assisted categorization
- System proposes categories for imported transactions.
- User can confirm/edit category decisions.
- Confirmed edits become reusable rules for future matching.

5. Budget caps and alerts
- User can define monthly category caps.
- System emits overspend warning when spend exceeds cap.

6. Error handling and retry
- Sync/categorization failures return actionable error messages.
- User can retry sync safely without data corruption.

## Non-Functional Requirements
- Local-first operation with no required cloud dependency for core workflows.
- Encrypted local data persistence.
- Deterministic ingestion behavior and duplicate prevention.
- Responsive category/budget calculations for at least 10,000 transactions.
- Observable operations with structured run outcomes for sync.

## Proposed Approach (High Level)
Architecture slices:
- Python service layer for connectors, normalization, categorization, and budgeting logic.
- Local encrypted SQLite-backed repository for accounts, transactions, category rules, and budgets.
- Connector abstraction for institution providers, starting with First Tech and Fidelity adapters.
- API/service endpoints for account linking, sync execution, categorization updates, budget management, and alert retrieval.

Data flow:
1. Link account -> persist account + connector metadata.
2. Run sync -> fetch institution records -> normalize -> deduplicate -> encrypt payload -> store.
3. Categorization -> propose category using learned rules/heuristics -> user confirms/edits.
4. Rule learning -> persist merchant-to-category rule from user decisions.
5. Budget evaluation -> aggregate monthly debits by category -> generate overspend alerts.

## Alternatives Considered
1. CSV-only ingestion first
- Rejected because user explicitly prioritizes institution connectivity now.

2. Cloud database first
- Rejected due local-only privacy boundary for MVP.

3. Full UI-first implementation before backend reliability
- Rejected to reduce risk; backend contract and correctness first enables iterative UI build.

## Risks, Mitigations, Open Questions
Risks:
- Institution connectivity inconsistencies.
- Categorization quality may lag initially.
- Key management friction for encrypted local storage.

Mitigations:
- Connector abstraction and per-provider actionable sync errors.
- Rule-learning loop from user corrections.
- Deterministic local key initialization with clear recovery guidance.

Open questions:
- Final quantitative threshold for acceptable miscategorization rate.
- Backup/restore UX for encrypted local storage.

## Dependencies
- Python runtime and packaging toolchain.
- Crypto library for local encryption.
- Test framework with coverage reporting.

## Migration / Rollout / Rollback Plan
Rollout:
- Enable baseline connectors, sync, categorization, and budget alerts for single user.

Rollback:
- If connector quality regresses, disable provider adapter while retaining local data.
- Preserve local user edits and rules across connector retries/fixes.

## Observability Plan
Track and expose:
- Sync request id, institution, start/end time, success/failure status.
- Imported record count and duplicate-skipped count.
- Categorization decision source (rule, heuristic, manual override).
- Budget alert counts by category and month.

## Test Strategy Summary
- Unit tests for normalization, deduplication, encryption/decryption, categorization learning, and budget alert logic.
- API/service integration tests for:
  - Linking First Tech and Fidelity
  - 90-day sync behavior
  - Category confirm/edit reuse
  - Overspend warning generation
  - Failure and retry semantics
- Coverage requirement: >=70% per module in this slice.
