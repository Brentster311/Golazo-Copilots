# SFI-018 — Architect Notes

## Architecture Review

### Scope Containment
- Change is isolated to `accia-s360/src/accia_s360/auth.py` (credential creation) + S360Reporter cleanup (LAUNCHME.ps1 removal, docs)
- No API contract changes, no new endpoints, no data model changes
- Blast radius: auth layer only — if it breaks, revert one commit

### Key Decisions
1. **Microsoft tenant ID hardcoded** (`72f988bf-86f1-41af-91ab-2d7cd011db47`) — this is a public value for the Microsoft corporate tenant. All S360 users are Microsoft employees.
2. **`s360_client/auth.py` untouched** — it's the older standalone package, not used by S360Reporter. Updating it would be scope creep.
3. **Type hint generalized** to `TokenCredential` protocol — future-proofs if we add more credential types.
4. **Error messages updated** — no more "run az login" suggestions since the app handles it.

### Failure Modes
| Failure | Behavior | Recovery |
|---------|----------|----------|
| CLI credential unavailable | Falls through to browser | Automatic |
| Browser login cancelled | `ClientAuthenticationError` raised | User sees error, can retry via Refresh |
| Browser login timed out | Same as cancelled | Same |
| Both fail | `S360AuthError` propagates to UI | Status bar shows "Authentication failed" |
| Localhost port in use (rare) | `InteractiveBrowserCredential` picks another port | Automatic |
