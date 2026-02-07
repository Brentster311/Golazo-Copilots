# SFI-018 — Project Owner Assistant Notes

## Decision Log

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | Browser-based interactive login (not device-code) | User confirmed — seamless experience on Windows desktop |
| 2 | `AzureCliCredential` first, `InteractiveBrowserCredential` as fallback | User wants zero-friction for developers who already use `az login`, but non-technical users who don't have Azure CLI should still be able to use the app |
| 3 | Remove `LAUNCHME.ps1` entirely | Script existed solely to run `az login` before launch — no longer needed |
| 4 | Single user story (not decomposed) | One user-observable outcome: "app handles its own auth" — fits in a single vertical slice |

## Clarifications Gathered

- **Q**: Browser or device-code login? **A**: Browser
- **Q**: Replace AzureCliCredential or fallback? **A**: Fallback — try CLI first, then interactive browser
- **Q**: Remove LAUNCHME.ps1? **A**: Yes, remove entirely

## Key Technical Context

- Current auth: `AzureCliCredential` only (in `accia-s360/src/accia_s360/auth.py`)
- Replacement: `ChainedTokenCredential(AzureCliCredential(), InteractiveBrowserCredential())`
- `azure-identity` already in dependencies — `InteractiveBrowserCredential` is available out of the box
- Two scopes in play: S360 API (`Service360/.default`) and MS Graph (`graph.microsoft.com/.default`)
- Both scopes must work through the chained credential
