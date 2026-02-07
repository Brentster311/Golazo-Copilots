# SFI-018 — In-App Azure Login

**Status**: BACKLOG

## User Story

- **Title**: In-App Azure Login with Browser Fallback
- **As a**: SFI Reporter user
- **I want**: the app to authenticate me automatically — using my existing `az login` session if available, or opening a browser login window if not
- **So that**: I can launch `SFIReporter.exe` directly without needing to run `az login` first or use the `LAUNCHME.ps1` script

## Out of Scope

- Device-code flow
- Token refresh UI (azure-identity handles this silently)
- Login to non-Microsoft tenants
- Storing credentials on disk (azure-identity manages its own token cache)

## Assumptions

- **Assumption (explicit)**: `azure-identity` `InteractiveBrowserCredential` is sufficient — it opens the system browser for AAD login and handles token caching. No MSAL direct usage needed.
- **Assumption (explicit)**: The `accia-s360` package's `AuthManager` currently only accepts `AzureCliCredential`. We will modify it to accept a `ChainedTokenCredential` that tries CLI first, then interactive browser.
- **Assumption (explicit)**: `LAUNCHME.ps1` can be deleted entirely since the app will handle auth. The zip will just contain `SFIReporter.exe` + `README.md`.

## Acceptance Criteria

- [ ] If user has a valid `az login` session, the app works exactly as before (no browser popup)
- [ ] If user has no `az login` session, a browser window opens for Microsoft login — after successful login the app loads data normally
- [ ] If the user cancels the browser login, a clear error message appears in the status bar (not a silent failure)
- [ ] `LAUNCHME.ps1` is removed from the repo; `BUILD_MANIFEST.md` and zip contents updated accordingly
- [ ] All existing tests continue to pass
- [ ] The exe builds and runs successfully with the new auth flow

## Non-Functional Requirements

- Auth attempt should time out after 120 seconds with a user-friendly message
- No additional user action beyond the browser login (no copy-paste codes)
- Token caching handled by azure-identity (subsequent launches within token lifetime skip login)

## Telemetry / Metrics Expected

- Log line: `"Auth method: AzureCliCredential"` or `"Auth method: InteractiveBrowserCredential"`
- Log line on failure: `"Authentication failed: <reason>"`

## Rollout / Rollback Notes

- Rollback: revert to previous commit, restore `LAUNCHME.ps1`
- No server-side changes required
