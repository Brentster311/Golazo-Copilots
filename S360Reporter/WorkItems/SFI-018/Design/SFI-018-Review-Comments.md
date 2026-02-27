# SFI-018 — Review Comments

## Design Review

### ✅ Strengths
- Single point of change (`accia-s360/auth.py`) — minimal blast radius
- `ChainedTokenCredential` is the right abstraction — explicit, fast, no magic
- Good call rejecting `DefaultAzureCredential` — its 8-method fallback chain is slow and produces confusing errors

### ⚠️ Recommendations

| # | Area | Comment | Severity |
|---|------|---------|----------|
| 1 | **Credential scope** | `InteractiveBrowserCredential` needs a `tenant_id` to avoid the "pick your org" prompt. The S360 scope implies `microsoft.onmicrosoft.com` tenant. Hardcode or resolve from config. | High |
| 2 | **Status feedback** | The design mentions "Signing in..." in the status bar but doesn't detail how. Since `ChainedTokenCredential.get_token()` blocks, the UI will freeze. Should run auth in the background thread (which `_do_refresh_work` already does). Confirm the first token request happens inside the thread, not on the UI thread. | Medium |
| 3 | **Error specificity** | Design says "clear error message" — should distinguish: (a) user cancelled browser, (b) auth timeout, (c) wrong tenant/no access. Map each to a distinct status message. | Medium |
| 4 | **PyInstaller bundling** | `InteractiveBrowserCredential` uses `http.server` for the localhost redirect. This is stdlib so should bundle fine, but also verify `webbrowser` module works from a frozen exe. | Medium |
| 5 | **`s360_client/auth.py` duplication** | There's a second `auth.py` at `src/s360_client/auth.py` that's nearly identical to the `accia-s360` one. Should it also get the chain, or is it dead code? | Low |
| 6 | **README update** | Design mentions updating README but doesn't list the specific sections to change. At minimum: remove `az login` from Requirements, update Usage, remove LAUNCHME.ps1 reference. | Low |

### Architecture Alignment
- No concerns — change is contained within the auth layer, no new patterns introduced.

---

## Architect Notes

### Approval
Design approved with the following binding decisions:

### Binding Decisions

| # | Decision | Detail |
|---|----------|--------|
| A1 | **Credential type annotation** | Change `_credential` type hint from `AzureCliCredential | None` to `TokenCredential | None` (the `azure.core.credentials` protocol). This keeps the contract generic. |
| A2 | **Tenant ID** | Pass `tenant_id="72f988bf-86f1-41af-91ab-2d7cd011db47"` (Microsoft corp tenant) to `InteractiveBrowserCredential`. Without this, users get a multi-org picker that's confusing. |
| A3 | **No changes to `s360_client/auth.py`** | That module is the older standalone client — S360Reporter uses `accia-s360` exclusively. Leave it as-is to avoid scope creep. |
| A4 | **Error suggestion text update** | The `S360AuthError` suggestion strings that say "Try running 'az login'" should be updated to say "Try clicking Refresh Data to re-authenticate" since the app now handles login. |
| A5 | **Logging contract** | Use logger name `accia_s360.auth`. Log lines: `"Auth: trying AzureCliCredential..."`, `"Auth: AzureCliCredential succeeded"`, `"Auth: CLI unavailable, trying InteractiveBrowserCredential..."`, `"Auth: InteractiveBrowserCredential succeeded"`, `"Auth: all credentials failed: <msg>"` |

### Security Review
- ✅ No tokens stored on disk by our code (azure-identity manages its own MSAL cache)
- ✅ No secrets in source — tenant ID is public
- ✅ Scopes are unchanged — principle of least privilege maintained
- ⚠️ `InteractiveBrowserCredential` starts a localhost HTTP server briefly for the OAuth redirect — this is standard and expected, but note it for firewall documentation
