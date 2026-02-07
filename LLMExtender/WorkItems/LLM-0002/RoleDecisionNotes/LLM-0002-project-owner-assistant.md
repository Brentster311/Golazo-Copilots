# Role Decision Notes: Project Owner Assistant

**Work Item:** LLM-0002  
**Role:** project-owner-assistant  
**Date:** 2026-02-07

---

## Decomposition Rationale

Split from `llm-extender-core`. See LLM-0001 decision notes for full rationale.

## Decisions

### 1. Config Fields Scope
Config stores: provider name, model name, auth strategy type, endpoint URL, and optional provider-specific params. Security artifacts are explicitly excluded from persistence.

### 2. YAML as Optional Dependency
`pyyaml` is an optional dependency to keep the core library lightweight. JSON works out of the box.

### 3. Secret Detection on Load
If a config file contains a field that looks like a secret (e.g., `api_key`, `token`, `secret`), the loader should raise an error or strip it with a warning. This is a safety net — config files should never have secrets in the first place.

## Open Questions
- None blocking.
