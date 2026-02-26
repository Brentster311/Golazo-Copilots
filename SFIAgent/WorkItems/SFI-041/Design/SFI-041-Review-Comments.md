# SFI-041 Review Comments

## Domain Expert Guidance

### Consulted Domain Experts
- API Integration/Contract Expert (S360 client + endpoint contract stability)
- Security/Auth Flow Expert (token lifecycle and error handling)
- Desktop Data Validation Expert (Tkinter input constraints + deterministic UX)

### Why Domain Expertise Is Required
This work item crosses multiple high-risk boundaries: a Windows Tkinter UX writes data to a backend API through a shared client abstraction, relies on token-based auth, and must preserve data integrity for action item ownership. These are contract-sensitive and failure-prone paths that benefit from explicit domain guidance before QA/architecture review.

### Domain Recommendations
1. API Contract Guardrails
   - Treat `save_action_owners` contract as strict and version-sensitive: require `KpiId`, `ServiceId`, `ActionItemId`, `SLAType`, `ActionOwnerAlias`, `ActionOwnerName` before submit.
   - Introduce a preflight payload validator at the app seam (before calling `get_client().save_action_owners(...)`) that returns categorized failures (missing-id, invalid-owner, contract-shape).
   - Normalize `SLAType` and owner alias/name casing and trim whitespace to avoid backend reject/ambiguity.

2. Auth/Reliability Behavior
   - Distinguish auth failures from transport failures in user messaging and telemetry:
     - auth/session expired -> actionable re-auth guidance
     - transient network/API -> retry guidance without implying persistence
   - Never update local UI state optimistically before a confirmed success response.
   - Ensure failed writes preserve prior owner display and keep modal state recoverable.

3. Data Validation Rules
   - Require both `ActionOwnerAlias` and `ActionOwnerName`; reject partial values.
   - Reject empty/whitespace-only values and aliases containing unsupported delimiters.
   - Enforce one-item save semantics in details dialog (single action item context only) to avoid accidental bulk contract misuse.

4. Tkinter UX Constraints (Windows)
   - Keep save affordance deterministic: disabled until required fields + IDs are valid.
   - Use explicit success/failure dialogs with non-technical language and no internal exception text.
   - Keep keyboard-only flow operable (`Tab`, `Enter`, `Esc`) to support non-technical operator efficiency.

5. Observability and Auditability
   - Emit one structured event per save attempt with outcome and category (`success`, `auth_failure`, `validation_failure`, `api_failure`, `network_failure`).
   - Include correlation-safe identifiers (`kpi_id`, `service_id`, `action_item_id`) and `duration_ms`; exclude tokens/secrets.
   - Track per-session successful owner saves for operational confidence in rollout.

### Key Risks and Constraints
- Contract Drift Risk: If S360 endpoint payload semantics change, GUI save can fail silently or misclassify errors.
  - Constraint: depend on `accia_s360` contract tests and explicit error mapping.
- Auth Expiry Risk: Expired token during modal session causes repeated failures and user confusion.
  - Constraint: detect and message auth issues distinctly; avoid generic “save failed” only.
- Data Integrity Risk: Alias/name mismatch could persist incorrect ownership mapping.
  - Constraint: validate pair consistency from source control/picker and block ambiguous edits.
- UI State Risk: Multiple rapid clicks can cause duplicate writes/race conditions.
  - Constraint: disable Save while in-flight; re-enable only after deterministic completion.

### Suggested Design Modifications
- Add a dedicated preflight validator function in SFIReporter layer to centralize required-field and payload-shape checks.
- Add explicit exception/result-to-category mapping for `save_action_owners` failures so message dialogs and logs remain consistent.
- Add in-flight guard for Save action (button disable + single request token) to prevent duplicate submissions.
- Add post-success state mutation contract: update only `ActionOwnerAlias` and `ActionOwnerName` after success confirmation, then trigger standard refresh path.

### Assumptions Made by Domain Experts
- The existing owner input control can provide both alias and display name reliably.
- `get_client()` remains the sole supported path for authenticated API interaction in GUI code.
- No new identity provider/auth model changes are in scope for this work item.

### Escalation Check
No fundamental design flaw requiring return to Program Manager was found. Guidance is compatible with current scope and improves contract/auth/data safety before implementation.

## Architect Notes

### Architectural Alignment and Boundaries
- Boundary is correct and should remain explicit: `dialogs.py` handles UI eventing only, `sfi_reporter.data` owns orchestration/validation and client access, and `accia_s360` owns HTTP/auth/session behavior.
- No direct GUI-to-HTTP path is permitted for this story; `get_client().save_action_owners(...)` remains the only write integration seam.
- Single-item save semantics in details dialog are architecturally preferred for this scope to limit blast radius and simplify failure isolation.

### API Contract Notes
- Persisted contract must be treated as strict input schema: `KpiId`, `ServiceId`, `ActionItemId`, `SLAType`, `ActionOwnerAlias`, `ActionOwnerName` are required and validated before submit.
- Contract normalization rules are approved: trim whitespace, reject empty values, and normalize `SLAType`/alias casing consistently before payload construction.
- Error contract at the app seam should emit stable categories (`validation_failure`, `auth_failure`, `network_failure`, `api_failure`, `unknown_failure`) to keep UI copy and telemetry deterministic.

### Failure Handling and Isolation
- Save flow must be single-flight (disable Save while request is in-flight) to prevent duplicate writes and race conditions.
- UI state mutation contract is approved: mutate `ActionOwnerAlias`/`ActionOwnerName` only after confirmed API success; on any failure, preserve prior owner values and show explicit non-technical error guidance.
- Failure isolation requirement: owner-save errors must not affect ETA editing/query builder paths or broader app session state.

### Auth and Privacy
- Auth posture remains unchanged and acceptable for this work item: use existing token-based `accia_s360` flow only, no new secrets or credentials.
- User messaging must distinguish auth expiry from transport/API failures; do not leak internal exception text, tokens, or stack traces to dialogs.
- Logging is approved only with correlation-safe identifiers (`kpi_id`, `service_id`, `action_item_id`) and duration/outcome metadata; no auth artifacts or sensitive payload details in logs.

### Rollback Safety (Action Owner Persistence)
- Rollback path is safe if it is feature-path scoped: remove/disable details-dialog save trigger while retaining read-only owner display.
- Backward compatibility expectation: no schema migration and no change to existing read flows; rollback must not alter cached owner display semantics outside this feature path.
- Operational rollback guardrail: if elevated write failures are detected, disable owner-write invocation and keep details modal usable for read/navigation.

### Default-Behavior Questions to Project Owner (Explicit)
1. For owner alias casing and whitespace normalization, should we preserve user-entered display formatting in UI while submitting normalized API values?
2. If API returns success but refresh fails, should modal show success with a follow-up “refresh may be stale” notice, or block success until refresh confirms?
3. On auth failure, should Save remain disabled until session refresh occurs, or remain enabled to allow immediate retry after re-auth?

### Architecture Decision and Escalation
- Decision: proceed within current story scope; no architectural change requiring a new user story is identified.
- Condition for escalation: if owner picker cannot reliably provide alias+name pair, create a new user story for identity resolution UX/contract hardening.
