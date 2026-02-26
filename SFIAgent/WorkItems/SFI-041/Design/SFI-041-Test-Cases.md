# SFI-041 Test Cases

## Scope
Validate Action Owner editing in SFIReporter details dialog for Windows-only GUI usage, persistence via `s360` client API, correct post-save refresh behavior, and deterministic user-facing failure handling.

## Assumptions
- Details dialog provides single-item context with required IDs: `KpiId`, `ServiceId`, `ActionItemId`, `SLAType`.
- Save path uses `get_client().save_action_owners(...)` (no direct GUI HTTP calls).
- Action Owner input/control provides both alias and display name.

## Acceptance Criteria Traceability Matrix
| AC ID | Acceptance Criterion | Covered By |
|---|---|---|
| AC-1 | Details dialog presents a clear Action Owner input/control. | TC-UI-001, TC-UI-002 |
| AC-2 | Valid save calls s360 API and receives success response. | TC-API-001, TC-API-002 |
| AC-3 | After successful save, refresh/reopen shows updated owner. | TC-REF-001, TC-REF-002 |
| AC-4 | On API failure, show user-friendly error and never show false success. | TC-ERR-001, TC-ERR-002, TC-ERR-003, TC-ERR-004 |
| AC-5 | Flow is GUI-only and operable by non-technical users. | TC-USAB-001, TC-USAB-002 |

## Test Cases

### UI / Details Dialog Control

#### TC-UI-001 — Action Owner control is present and understandable
- **Maps to:** AC-1
- **Level:** GUI/integration
- **Preconditions:** Open SFIReporter on Windows; open details dialog for one action item.
- **Steps:**
  1. Observe details dialog fields and controls.
  2. Locate Action Owner label/control.
  3. Verify save affordance is visually associated with Action Owner edit.
- **Expected:**
  - Action Owner control is visible, labeled clearly, and placed in normal dialog flow.
  - Control supports selecting/entering a valid owner pair (alias + display name).
- **Failure message (test assertion):** `Expected Action Owner control to be visible and clearly labeled in details dialog.`

#### TC-UI-002 — Save affordance is deterministic
- **Maps to:** AC-1, AC-5
- **Level:** GUI/integration
- **Preconditions:** Details dialog open.
- **Steps:**
  1. Leave Action Owner empty/invalid and observe Save state.
  2. Enter valid Action Owner pair and observe Save state.
- **Expected:**
  - Save is disabled when required data is invalid or incomplete.
  - Save is enabled when required owner + IDs are present.
- **Failure message (test assertion):** `Expected Save button state to track Action Owner validity deterministically.`

### API Save Path

#### TC-API-001 — Valid save calls `save_action_owners` with required contract fields
- **Maps to:** AC-2
- **Level:** Unit/integration seam (mocked client)
- **Preconditions:** Mock `get_client()` and `save_action_owners` success response.
- **Steps:**
  1. Trigger Save with valid Action Owner + item context.
  2. Capture invoked arguments.
- **Expected:**
  - `save_action_owners` called exactly once.
  - Call includes `kpi_id`, `action_owner_alias`, `action_owner_name`, and one-item `action_items` list containing `ServiceId`, `ActionItemId`, `SLAType`.
- **Failure message (test assertion):** `Expected exactly one save_action_owners call with required S360 payload fields.`

#### TC-API-002 — No direct HTTP from GUI layer during save
- **Maps to:** AC-2
- **Level:** Unit/static seam test
- **Preconditions:** Instrument/patch HTTP entry points used elsewhere.
- **Steps:**
  1. Trigger Action Owner save from dialog callback.
  2. Assert only `get_client().save_action_owners` path is used.
- **Expected:**
  - GUI code does not make raw HTTP calls for Action Owner persistence.
- **Failure message (test assertion):** `Expected GUI save flow to use s360 client abstraction only (no raw HTTP).`

### Post-Save Refresh / Data Correctness

#### TC-REF-001 — Success updates in-memory owner state only after confirmed success
- **Maps to:** AC-3
- **Level:** Unit/integration seam
- **Preconditions:** Item starts with old owner values; mock success response.
- **Steps:**
  1. Save new Action Owner.
  2. Observe in-memory item fields and success feedback timing.
- **Expected:**
  - `ActionOwnerAlias` and `ActionOwnerName` mutate only after success.
  - Success feedback appears once, post-confirmation.
- **Failure message (test assertion):** `Expected owner fields to update only after confirmed save success.`

#### TC-REF-002 — Reopen/refresh displays persisted Action Owner
- **Maps to:** AC-3
- **Level:** GUI/integration
- **Preconditions:** One successful save already completed.
- **Steps:**
  1. Close details dialog.
  2. Reopen same item OR trigger item refresh path then open details.
- **Expected:**
  - Displayed Action Owner matches saved value (alias/name as designed).
- **Failure message (test assertion):** `Expected refreshed/reopened details to show persisted Action Owner value.`

### Failure Messaging / Error Handling

#### TC-ERR-001 — Auth failure message is user-friendly and actionable
- **Maps to:** AC-4
- **Level:** Integration seam (mock auth exception)
- **Preconditions:** Mock `save_action_owners` to raise auth/session-expired condition.
- **Steps:** Trigger Save.
- **Expected:**
  - User sees non-technical auth guidance (e.g., re-auth/refresh session).
  - No success indicator shown.
  - Owner fields remain unchanged.
- **Failure message (test assertion):** `Expected auth failure dialog with actionable non-technical guidance and no false success state.`

#### TC-ERR-002 — Validation failure blocks API call and explains fix
- **Maps to:** AC-4
- **Level:** Unit + GUI
- **Preconditions:** Missing/invalid alias or name.
- **Steps:** Attempt Save.
- **Expected:**
  - API save is not called.
  - User sees clear message to correct Action Owner input.
  - No success indicator shown.
- **Failure message (test assertion):** `Expected validation error to block API call and present corrective message.`

#### TC-ERR-003 — Network/API failure message is user-friendly and non-deceptive
- **Maps to:** AC-4
- **Level:** Integration seam
- **Preconditions:** Mock transport/API failure.
- **Steps:** Trigger Save.
- **Expected:**
  - User sees understandable failure message with retry guidance.
  - No success indicator shown.
  - Existing owner value remains displayed.
- **Failure message (test assertion):** `Expected network/API failure message with retry guidance and preserved prior owner display.`

#### TC-ERR-004 — Unknown exception path remains safe for users
- **Maps to:** AC-4
- **Level:** Integration seam
- **Preconditions:** Mock unexpected exception type.
- **Steps:** Trigger Save.
- **Expected:**
  - Generic user-friendly error shown (no raw stack trace/internal exception text).
  - No false success; no owner mutation.
- **Failure message (test assertion):** `Expected unknown failure to surface safe user-facing error without internal exception leakage.`

### GUI-Only Usability for Non-Technical Users

#### TC-USAB-001 — End-to-end owner update requires only GUI actions
- **Maps to:** AC-5
- **Level:** Manual/UAT script (Windows)
- **Preconditions:** App running with authenticated session.
- **Steps:**
  1. Open item details dialog.
  2. Change Action Owner.
  3. Save and verify success.
  4. Reopen item and confirm new owner.
- **Expected:**
  - Scenario completes entirely in GUI with no CLI/script/backend steps.
- **Failure message (test assertion):** `Expected full Action Owner update workflow to complete via GUI-only interactions.`

#### TC-USAB-002 — Keyboard-driven usability remains operable
- **Maps to:** AC-5
- **Level:** Manual GUI accessibility/usability
- **Preconditions:** Details dialog open.
- **Steps:**
  1. Use `Tab` to reach Action Owner control and Save.
  2. Use `Enter` to submit (when valid).
  3. Use `Esc` to cancel/close without save.
- **Expected:**
  - Keyboard-only flow is deterministic and usable for non-technical users.
- **Failure message (test assertion):** `Expected keyboard-only Action Owner edit/save flow (Tab/Enter/Esc) to be operable.`

## Non-Functional / Reliability Checks
- Verify Save action is single-flight (no duplicate submissions while request is in-flight).
- Verify telemetry events per attempt include outcome category and duration.
- Verify logs do not include secrets/tokens.

## Capability Coverage Check (from `capabilities.yaml` impact)
Directly affected capabilities:
- `reporter-data` — covered by TC-API-001, TC-REF-001, TC-ERR-002.
- `accia-s360-client` — covered by TC-API-001 and failure-path tests TC-ERR-001/003/004.

Transitively affected capabilities (no contract changes expected in this story):
- `reporter-tk-app` — covered by TC-UI/REF/ERR/USAB GUI cases.
- `reporter-tests` — this artifact defines required additions.
- `reporter-eta-logic`, `reporter-query-builder`, `reporter-llm`, `reporter-build`, `accia-s360-tests` — regression risk only; include targeted smoke regression to confirm no unintended breakage.

## Exit Criteria for QA Sign-off
- Every AC (AC-1..AC-5) has at least one passing test.
- Failure paths do not show false success and preserve prior owner display.
- GUI-only scenario passes on Windows with non-technical test script.
- No uncovered capability contract gaps remain for direct dependencies.
