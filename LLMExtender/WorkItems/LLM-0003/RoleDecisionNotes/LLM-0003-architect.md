# Architect Decision Notes: LLM-0003

**Work Item:** LLM-0003  
**Role:** Architect  
**Date:** 2026-02-07

---

## Decisions

### A1: Wrap callback exceptions in `AuthenticationError` (QA R2 accepted)
**Problem:** If a user-supplied callback raises, the raw exception would leak through.  
**Decision:** `CallbackAuth.resolve()` and `aresolve()` wrap any callback exception in `AuthenticationError` with the original as `__cause__`.  
**PO Approval:** Yes

### A2: Defer MSI async optimization (QA R1 — defer)
**Problem:** `ManagedIdentityAuth.aresolve()` creates a new `AsyncManagedIdentityCredential` per call.  
**Decision:** Accept for correctness within this story's scope. Lazy async credential lifecycle is future work.  
**PO Approval:** Yes

### A3: `AuthenticationError` inherits from `LLMExtenderError`
**Decision:** Consistent with exception hierarchy from LLM-0001. Callers can catch `LLMExtenderError` for all library errors.  
**PO Approval:** Yes

### A4: Client integration in scope — resolve auth eagerly in `LLMClient.__init__`
**Problem:** How does the auth strategy feed into the provider?  
**Decision:** `LLMClient.__init__` gains `auth: AuthStrategy | None = None`. If provided, `auth.resolve()` is called immediately and the resolved key is used as `api_key` for provider construction. This is a sync-only resolution at init time.  
**Trade-off:** Token refresh requires re-creating the client. Acceptable — no key rotation in scope.  
**Backward-compatible:** If no `auth` is passed, `config.api_key` is used as before. All LLM-0001 tests pass unchanged.  
**PO Approval:** Yes

### A5: `api_key` default changes to `""`
**Problem:** Currently `api_key` is required (no default). With auth strategies, users may not have a key at construction time.  
**Decision:** `api_key: str = field(default="", repr=False)`. LLM-0001 tests all pass `api_key` explicitly, so nothing breaks.  
**PO Approval:** Yes
