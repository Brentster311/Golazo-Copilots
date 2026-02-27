# SFI-027 — MS Graph People Hierarchy in accia-s360

**Status**: IMPLEMENTED

## User Story

- **Title**: Add MS Graph-based People Hierarchy to accia-s360
- **As a**: developer using the accia-s360 library
- **I want**: a new capability that queries Microsoft Graph API to retrieve a person's full org hierarchy (managers above and direct reports below)
- **So that**: consumers (like S360Reporter) can accurately map any user's org tree without relying on S360's limited hierarchy APIs which only return shallow team IDs

- **Out of scope**:
  - Changes to S360Reporter's `tk_app.py` or any consumer code (that's SFI-026)
  - Caching/persistence of org data (consumers handle their own caching)
  - Resolving non-EA / SC ALT accounts (filter them out)
  - Org trees deeper than 10 levels in either direction
  - Batch/delta sync or webhook subscriptions

- **Assumptions**:
  - **Assumption (explicit)**: The existing `get_graph_token()` in `accia_s360.auth.AuthManager` already acquires tokens with sufficient Graph scope (`https://graph.microsoft.com/.default`) to call `/users/{id}/manager` and `/users/{id}/directReports`. Confirmed by live POC.
  - **Assumption (explicit)**: Graph API User.Read.All or Directory.Read.All permissions are available via the Azure CLI credential chain. Confirmed by live POC showing manager chain and direct reports for muralic.
  - **Assumption (explicit)**: Direct reports filtering should exclude non-EA SC ALT accounts (aliases matching `sc-*` or `SC-*` patterns) since they are shadow accounts.
  - **Assumption (explicit)**: The new capability lives in `accia_s360/endpoints/` as a new module alongside existing endpoint modules (`extended.py`, `action_items.py`, etc.).

## Acceptance Criteria (bulleted, testable)

- [ ] **AC-1**: `client.get_manager_chain(alias)` returns an ordered list of managers from immediate manager up to CEO, each with `display_name`, `alias`, `job_title`, and `department`.
- [ ] **AC-2**: `client.get_direct_reports(alias)` returns a list of direct reports with `display_name`, `alias`, `job_title`, and `department`. SC ALT accounts are excluded.
- [ ] **AC-3**: `client.get_org_tree(alias, depth=2)` returns a nested structure: the target user, their direct reports, and each direct's reports (configurable depth, default 2). SC ALT accounts are excluded.
- [ ] **AC-4**: All three methods raise `S360AuthError` on authentication failures and handle Graph API rate limiting (429) with retry.
- [ ] **AC-5**: Unit tests cover all three methods with mocked Graph responses (manager chain, direct reports, nested org tree, error cases).
- [ ] **AC-6**: At least one live integration test confirms `get_manager_chain('muralic')` returns a chain containing `alexhowells` and `get_direct_reports('muralic')` includes `brentj`.

## Non-functional requirements
- Graph API calls should respect HTTP 429 rate limiting with exponential backoff (max 3 retries)
- Each method should have a configurable timeout (default from `S360Config.timeout_seconds`)
- Results returned as typed dataclasses/NamedTuples, not raw dicts

## Telemetry / metrics expected
- Logging at INFO level for each Graph API call (alias being queried)
- Logging at WARNING level for retries due to rate limiting
- Logging at ERROR level for auth or unexpected failures

## Rollout / rollback notes
- This is a new additive capability — no breaking changes to existing accia-s360 API surface
- Consumers opt-in by calling the new methods
- Rollback: simply don't call the new methods; existing S360-based hierarchy continues to work
