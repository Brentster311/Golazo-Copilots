# Role Decision Notes: Program Manager

**Work Item:** LLM-0002  
**Role:** program-manager  
**Date:** 2026-02-07

---

## Decisions

### 1. Dataclass over Pydantic
Stdlib `dataclass` keeps the library lightweight with zero extra dependencies. Pydantic adds validation niceties but is a heavy dependency for a config object.

### 2. Secret Field Detection by Name
Using a `frozenset` of known secret field names (`api_key`, `token`, `secret`, etc.) to detect secrets in loaded config files. Simple and effective. Not bulletproof (user could put a key in `extra`), but covers the primary use case and matches the user's intent.

### 3. JSON via Stdlib, YAML via Optional pyyaml
JSON is always available. YAML requires `pyyaml` as an optional dep. This keeps the core dependency-free while supporting the user's requirement for both formats.

### 4. No Version Field Yet
Considered adding a `version` field to serialized config for future migration. Deferred — can be added when needed without breaking changes.

## Open Questions
- None blocking.
