# Refactor Decision Notes: LLM-0003

**Work Item:** LLM-0003  
**Role:** Refactor Expert  
**Date:** 2026-02-07

---

## Changes Made

1. **Fixed stale `_config`** — When `auth` is provided, `self._config` now stores the resolved copy (with `api_key` set) instead of the original.
2. **Moved `dataclasses.replace` import to top level** — stdlib import was inline; moved for consistency.
3. **Removed redundant `__str__` overrides** — `EnvVarAuth`, `CallbackAuth`, `ManagedIdentityAuth` all had `__str__` that just called `__repr__`. Python's default `__str__` already does this. Base class `AuthStrategy.__str__` handles the delegation.
4. **Suppressed noisy `ImportError` chains** — `ManagedIdentityAuth.__init__` and `aresolve` now use `from None` to avoid confusing "During handling of..." messages.
5. **Extracted `_validate` helper in `CallbackAuth`** — DRYed up the duplicate empty-result check in `resolve()` and `aresolve()`.

## Verification

- 53/53 tests passing before and after refactoring
- No behavior changes
