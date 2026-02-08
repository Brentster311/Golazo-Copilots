# LLM-0005 — Architect Notes
- Architecture approved. Follows `AuthStrategy` ABC contract exactly.
- Chain pattern is explicit and testable — no hidden credential types.
- `scope` parameter is the right abstraction for cross-story reuse.
- Lazy import of `azure-identity` maintains optional-dependency contract.
- Async lifecycle: credentials created and closed per call to avoid leaks.
- No architectural concerns. Proceed to implementation.
