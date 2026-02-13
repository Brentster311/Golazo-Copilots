# EES-00008 — Program Manager Decision Notes

## Key Decisions

### Single work item for A+C
Combined prompt tuning and scope field into one deliverable. They're two sides of the same coin — prompt reduces noise, scope field catches what slips through. Neither is useful in isolation.

### Scope as orthogonal to status
`scope` (rule/context) and `status` (confirmed/rejected) are independent dimensions. A context fact can still be confirmed — it just means "yes this is true, but don't build rules from it." This avoids overloading the status field.

### Default to "rule" for backward compatibility
Old Fact dicts without `scope` default to `"rule"`. This means existing saved incidents and tests continue to work without modification. Conservative choice — better to include a fact in rules by default than silently drop it.

### No changes to RuleEvaluator
The evaluator works on stored rules, which already have their conditions baked in. The scope filtering happens at rule *creation* time (in _save_all), not evaluation time. Clean separation.

### Prompt approach: instruction-based, not few-shot
Added explicit DO/DON'T lists rather than few-shot examples. The existing prompt is already instruction-heavy; adding examples would make it too long and risk confusing the JSON schema section.
