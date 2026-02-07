# Role Decision Notes: Project Owner Assistant

**Work Item:** LLM-0003  
**Role:** project-owner-assistant  
**Date:** 2026-02-07

---

## Decomposition Rationale

Split from `llm-extender-core`. See LLM-0001 decision notes for full rationale.

## Decisions

### 1. Three Initial Auth Strategies
- **EnvVarAuth** — simplest, covers local dev and CI. Reads a named env var.
- **ManagedIdentityAuth** — Azure MSI for cloud deployments. Uses `azure-identity` as optional dep.
- **CallbackAuth** — escape hatch for custom mechanisms (key vaults, custom APIs, etc.). Accepts any `() -> str` callable.

### 2. Security as Non-Negotiable
User explicitly stated: do not store or log security artifacts. This is enforced at multiple levels:
- `__repr__`/`__str__` mask credentials
- No logging of credential values at any level
- No serialization of credentials to disk

### 3. azure-identity as Optional
`ManagedIdentityAuth` requires `azure-identity`, but it's an optional dependency. Users who don't need Azure MSI don't need to install it.

## Open Questions
- None blocking.
