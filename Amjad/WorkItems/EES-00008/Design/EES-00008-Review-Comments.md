# EES-00008 — Design Review Comments

## Overall Assessment
Design is clear, well-scoped, and implementable. No blockers.

## Minor Observations

### 1. Scope field in LLM JSON schema
The design doc says "LLM JSON output includes `scope` per fact" but the current `_SYSTEM_PROMPT` defines a specific JSON schema. The schema section needs to be updated to show `"scope": "rule"|"context"` in the facts array. Not a gap — just an implementation detail to not forget.

### 2. GUI toggle mechanism
Design says "toggle capability" but doesn't specify the interaction. Recommendation: add a "Set Rule" / "Set Context" button pair next to the existing Confirm/Reject buttons, consistent with the existing UI pattern.

### 3. Transitively affected capabilities
Impact analysis shows `yaml-persistence`, `rule-evaluation`, `cli-orchestration`, and `ontology-management` are transitively affected. However:
- **yaml-persistence**: No changes needed — `scope` is just another dict key, handled by existing `to_dict()`/`from_dict()`
- **rule-evaluation**: No changes needed — evaluates stored rules, not facts
- **cli-orchestration**: Should filter by scope same as GUI `_save_all` does. **Risk**: if CLI `main.py` also calls RuleGenerator, it needs the same scope filter. Verify.
- **ontology-management**: No changes needed — uses facts to update ontology regardless of scope

### 4. `to_condition_dict()` should NOT include scope
The `to_condition_dict()` method is used for serializing facts into rule conditions. Since scope is a classification concern (not a matching concern), it should be excluded from `to_condition_dict()` but included in `to_dict()`.

## No Blockers
Design is approved for implementation.

---

## Architect Notes

### Architectural Alignment
The change is well-contained. The `scope` field is a leaf addition to the `Fact` dataclass — it doesn't alter any inter-module contracts. The `Fact` serialization contract (`to_dict()`/`from_dict()`) gains an optional key with a safe default.

### Data Contract
- `Fact.to_dict()`: gains `"scope"` key (always present)
- `Fact.from_dict()`: reads `"scope"` with `d.get("scope", "rule")` — backward compatible
- `Fact.to_condition_dict()`: must NOT include scope — agreed with QA
- LLM JSON schema: `"scope"` is optional in output; parser defaults to `"rule"`

### Security/Privacy
No concerns — scope is a classification label, not sensitive data.

### Blast Radius
- **Direct**: models.py, fact_extractor.py, app.py, adapters.py
- **Indirect**: main.py (CLI) needs same scope filter at `filter_rules` call site
- **Safe**: yaml_store.py, rule_evaluator.py, ontology_manager.py — no changes needed

### TechBestPractices Compliance
No new Azure/cloud integrations. No new dependencies. Compliant.

### Rollback Safety
Removing the `scope` field from code leaves orphaned `scope` keys in YAML files. These are harmless — `from_dict()` ignores unknown keys via `d.get()`. Safe rollback.
