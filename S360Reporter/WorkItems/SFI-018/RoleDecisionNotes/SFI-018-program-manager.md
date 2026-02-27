# SFI-018 — Program Manager Notes

## Design Decisions

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | `ChainedTokenCredential` over `DefaultAzureCredential` | Default tries ~8 methods (managed identity, env vars, etc.) — slow on failure and confusing errors. Chaining just CLI + browser is explicit and fast. |
| 2 | Change in `accia-s360` auth layer, not in S360Reporter | All S360 API calls flow through `AuthManager` — single point of change |
| 3 | No custom token persistence | azure-identity manages its own cache; no need to duplicate |
| 4 | 120-second auth timeout | Generous enough for slow browser + MFA, short enough to not feel hung |

## Risk Assessment

Primary risk is PyInstaller not bundling `InteractiveBrowserCredential`'s dependencies (it uses `http.server` internally for the redirect). Mitigation: test the exe build early in the developer phase.
