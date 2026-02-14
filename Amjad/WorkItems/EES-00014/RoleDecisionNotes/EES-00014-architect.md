# EES-00014 — Architect Notes

## Decisions
1. No new architecture — pure removal of two redundant features.
2. Backward compat is naturally handled by `d.get()` patterns in `from_dict` — no special migration code needed.
3. `Incident.root_cause_identified` stays (out of scope) — incidents can still record root causes manually.
4. `_confirm_root_cause` in `main.py` must be removed or simplified since `LLMResponse` will no longer carry `root_cause`.

## Capability Impact
- 8 capabilities affected (3 direct, 5 transitive). All have existing test coverage.
