# EES-00008 — Architect Decision Notes

## Decisions

### No structural changes needed
The `scope` field is a leaf addition. No new modules, no new interfaces, no new dependencies. The existing Fact serialization pattern (`to_dict`/`from_dict` with `d.get()` defaults) naturally supports backward compatibility.

### `to_condition_dict()` exclusion confirmed
Scope is orthogonal to fact identity. A fact used as a rule condition should never carry its scope classification — conditions are evaluated by value matching, not by how they were originally classified.

### CLI parity required
Confirmed that `main.py` line 249 passes `confirmed_facts` to `gen.filter_rules()`. The developer must add the same scope filter here: `rule_facts = [f for f in confirmed_facts if f.scope == "rule"]`.

### No changes to RuleEvaluator
Verified that `RuleEvaluator.evaluate()` works on stored rule conditions, not on raw facts. Scope filtering at rule creation time is sufficient.

### TechBestPractices reviewed
No violations. No new Azure integrations, no new credential patterns, no direct Kusto usage.
