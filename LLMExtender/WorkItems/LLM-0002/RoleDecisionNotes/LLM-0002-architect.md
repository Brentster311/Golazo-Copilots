# Architect Decision Notes: LLM-0002

**Work Item:** LLM-0002  
**Role:** Architect  
**Date:** 2026-02-07

---

## Decisions

### A1: Merge config shapes — preserve backward compatibility
**Problem:** Design doc defines `LLMConfig` with `provider`, `model`, `auth_strategy`, `base_url`, `extra`. Existing LLM-0001 code has `provider`, `model`, `api_key`, `base_url`, `timeout`. These are incompatible.  
**Decision:** Merge both shapes. Add `auth_strategy` and `extra` as new fields with defaults. Keep `api_key` (default `""`, `repr=False`, never serialized) and `timeout`. LLM-0001's 30 tests remain green without changes.  
**PO Approval:** Yes

### A2: Scan `extra` dict for secrets (QA R1 accepted)
**Problem:** Users may put secrets in the `extra` dict.  
**Decision:** `SECRET_FIELD_NAMES` check applies to both top-level file keys AND keys inside the `extra` dict on load.  
**PO Approval:** Yes

### A3: Unknown fields on load — silently ignore (QA R2 modified)
**Problem:** QA R2 suggests warning on unknown fields.  
**Decision:** Silently ignore unknown non-secret keys. Libraries should not emit warnings that clutter consumer output. Unknown keys are filtered during construction.  
**PO Approval:** Yes

### A4: Serialization exclusion list
**Decision:** `to_json` / `to_yaml` serialize all fields EXCEPT `api_key`. `timeout`, `extra`, `auth_strategy` are all safe to persist.  
**PO Approval:** Yes

### A5: Field ordering
**Decision:** `provider`, `model`, `api_key` (default `""`), `auth_strategy` (default `""`), `base_url` (default `None`), `timeout` (default `30.0`), `extra` (default `field(default_factory=dict)`). `api_key` gets `default=""` so all subsequent fields can have defaults.  
**PO Approval:** Yes
