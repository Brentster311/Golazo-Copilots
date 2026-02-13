# EES-00008 — Quality Assurance Decision Notes

## Decisions

### Impact analysis review
8 capabilities affected (4 direct, 4 transitive). Verified that transitive capabilities (yaml-persistence, rule-evaluation, ontology-management) need no code changes. CLI orchestration needs the same scope filter as the GUI — flagged in review comments.

### `to_condition_dict()` must exclude scope
Scope is a classification concern, not a matching concern. Rule conditions should never contain scope — it would break rule evaluation.

### CLI parity flagged
The CLI `main.py` also passes confirmed_facts to `RuleGenerator.filter_rules()`. The scope filter must be applied there too, or context facts will leak into CLI-generated rules. Flagged for developer attention.

### Test coverage
12 test cases covering all 7 acceptance criteria. Every AC has at least one test. Added backward compatibility tests (TC-5, TC-8) since the scope field is new and old data must still work.
