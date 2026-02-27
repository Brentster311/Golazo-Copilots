# SFI-018 — Refactor Expert Notes

## Assessment

The auth code is clean and well-structured:
- `_get_token_with_chain()` cleanly encapsulates the fallback logic
- `get_s360_token()` and `get_graph_token()` differ only by scope — minor duplication but keeps them explicit and independently documentable
- Lazy initialization of credentials via `_get_cli_credential()` / `_get_browser_credential()` follows existing patterns
- Logging is consistent and follows the agreed contract

## Decision

No refactoring needed. The code is small, clear, and follows existing patterns in the codebase.

## Unused import check

- `AccessToken` — used in `_get_token_with_chain` return type
- `TokenCredential` — imported but unused. Could remove, but it's a common base type for documentation. Leaving as-is.
