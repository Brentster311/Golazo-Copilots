# Review Comments: LLM-0002

**Work Item:** LLM-0002  
**Reviewer:** Quality Assurance  
**Date:** 2026-02-07

---

## Design Clarity & Completeness

### ✅ Strengths
1. **Clear secret field guard** — `SECRET_FIELD_NAMES` frozenset is simple and auditable.
2. **JSON via stdlib, YAML via optional dep** — minimizes required dependencies.
3. **Config has no secret fields by design** — secrets live in auth (LLM-0003), not config.

### ⚠️ Recommendations

**R1: Handle `extra` dict containing secrets**
- The risk table acknowledges users might put secrets in `extra`. The secret field scan should also check keys in the `extra` dict, not just top-level keys of the loaded file.
- **Recommendation:** On load, also scan `extra` keys against `SECRET_FIELD_NAMES`.
- **Severity:** Medium — security gap.

**R2: from_json / from_yaml should reject unknown fields**
- If a JSON file has fields not in the dataclass, what happens? Silent ignore? Error?
- **Recommendation:** Log a warning for unknown fields (typo protection) but don't error. Use `**kwargs` filtering into known fields.
- **Severity:** Low — usability improvement.

**R3: Path type consistency**
- Methods accept `str | Path`. Good. Ensure all internal path handling uses `Path` for consistency.
- **Severity:** Low — code hygiene.

**R4: Config equality**
- Dataclass auto-generates `__eq__`. Verify this is the desired behavior for round-trip testing.
- **Severity:** Low — test infrastructure.

## Feasibility & Sequencing
- ✅ No concerns. Stdlib-heavy implementation.

## Risk Coverage
- ✅ Secret detection covered.
- ⚠️ `extra` dict scanning (see R1).

## Naming Clarity
- ✅ `LLMConfig`, `from_json`, `to_yaml`, `SecretInConfigError` — all clear.

---

## Architect Notes

**Date:** 2026-02-07

| Decision | Disposition |
|---|---|
| R1 (scan `extra` for secrets) | **Accepted.** Secret scan checks both top-level and `extra` keys. |
| R2 (reject/warn unknown fields) | **Modified.** Silently ignore unknown fields — library should not emit warnings. |
| R3 (Path consistency) | **Accepted.** Internal handling uses `Path`. |
| R4 (Config equality) | **Accepted.** Dataclass `__eq__` is correct for round-trip testing. |

**Additional decisions:**
- A1: Merge LLM-0001 and LLM-0002 config shapes. Keep `api_key`, `timeout` for backward compatibility. Add `auth_strategy`, `extra`.
- A4: `api_key` is NEVER serialized to disk. All other fields are safe.
- A5: Field order: `provider`, `model`, `api_key` (default `""`), `auth_strategy` (default `""`), `base_url`, `timeout`, `extra`.
