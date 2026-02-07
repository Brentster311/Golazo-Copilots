# SFI-018 — Design Doc: In-App Azure Login

## Summary

Replace the external `az login` dependency with an in-app authentication flow. The app will try `AzureCliCredential` first (zero friction for developers), then fall back to `InteractiveBrowserCredential` (opens system browser for Microsoft login). `LAUNCHME.ps1` will be removed.

## Problem Statement

Users must run `az login` in a PowerShell terminal before launching SFI Reporter. This creates friction:
- Non-technical users don't know what `az login` is
- The `LAUNCHME.ps1` wrapper is easy to skip — launching the exe directly fails silently
- Expired tokens cause confusing "all zeros" data with no clear error

## Business Case

- **Why now**: The app is being distributed to team leads who aren't developers — they shouldn't need Azure CLI
- **Impact**: Eliminates the #1 support question ("why is everything zero?")
- **KPIs**: Zero auth-related support requests after rollout

## Stakeholders

| Role | Person |
|------|--------|
| Product Owner | Brent |
| Developer | Copilot |
| Users | ACCIA service owners & managers |

## Functional Requirements

1. **Credential chain**: `AzureCliCredential` → `InteractiveBrowserCredential`
2. **Browser login**: If CLI credential fails, open system browser for Microsoft AAD login
3. **Both scopes**: S360 API and MS Graph must work through the chain
4. **Error handling**: Clear status bar message if auth fails or is cancelled
5. **Remove LAUNCHME.ps1**: Delete from repo and from zip contents

## Non-Functional Requirements

- Auth timeout: 120 seconds
- No new external dependencies (azure-identity already installed)
- Token caching by azure-identity (no custom persistence)
- Log which credential method succeeded

## Proposed Approach

### Layer 1: `accia-s360/src/accia_s360/auth.py`

Replace the `AzureCliCredential()` instantiation with a `ChainedTokenCredential`:

```python
from azure.identity import (
    AzureCliCredential,
    ChainedTokenCredential,
    InteractiveBrowserCredential,
)

credential = ChainedTokenCredential(
    AzureCliCredential(),
    InteractiveBrowserCredential(),
)
```

This is the only code change needed — `ChainedTokenCredential` tries each in order and uses the first that succeeds. All downstream code (`get_s360_token`, `get_graph_token`) already calls `credential.get_token(scope)` which works identically.

### Layer 2: `sfi_reporter/tk_app.py`

- Improve error handling in `_do_refresh_work()` to detect auth failures and show a specific "Authentication failed" message instead of generic "Error loading data"
- Add a status bar message "Signing in..." while auth is in progress

### Layer 3: Cleanup

- Delete `LAUNCHME.ps1`
- Update `BUILD_MANIFEST.md` (remove LAUNCHME.ps1 from zip contents)
- Update `README.md` (remove references to `az login` as a prerequisite, mention browser login)

## Alternatives Considered

| Alternative | Verdict | Reason |
|-------------|---------|--------|
| Device-code flow | Rejected | User wants seamless browser experience |
| MSAL directly | Rejected | azure-identity wraps MSAL — simpler API, already a dependency |
| `DefaultAzureCredential` | Rejected | Tries too many methods (managed identity, env vars, VS Code) — slow and confusing error messages |
| Keep LAUNCHME.ps1 as optional | Rejected | User wants it removed — in-app login makes it redundant |

## Risks & Mitigations

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Browser popup blocked by corporate policy | Low | Falls back gracefully; log clear error message |
| InteractiveBrowserCredential not bundled by PyInstaller | Medium | Add as hidden-import if needed; test in exe build |
| Token cache conflict between CLI and browser | Low | azure-identity handles separate caches per credential type |

## Open Questions

None — all clarified with product owner.

## Dependencies

- `azure-identity` >= 1.14.0 (already installed — has `InteractiveBrowserCredential`)
- No new pip packages

## Migration / Rollout / Rollback

- **Rollout**: Build new exe, distribute zip
- **Rollback**: Revert commit, restore `LAUNCHME.ps1`, rebuild exe
- **Migration**: None — stateless change

## Observability

- Log: `"Auth: trying AzureCliCredential..."` / `"Auth: AzureCliCredential succeeded"` / `"Auth: falling back to InteractiveBrowserCredential"`
- Log: `"Auth failed: <exception>"`

## Test Strategy

- Unit test: mock credential chain, verify fallback behavior
- Unit test: verify auth failure produces user-facing error message
- Integration: manual test — run exe without `az login`, confirm browser opens
- Integration: manual test — run exe with valid `az login`, confirm no browser popup
- Build test: verify exe bundles InteractiveBrowserCredential correctly
