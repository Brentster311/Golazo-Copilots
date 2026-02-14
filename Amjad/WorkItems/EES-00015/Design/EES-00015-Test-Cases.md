# EES-00015 — Test Cases

## TC-01: facts_used_by_rules returns correct indices
- Given 3 facts and 1 rule referencing fact[0] and fact[2]
- When `facts_used_by_rules(facts, rules)` is called
- Then returns `{0, 2}`

## TC-02: Chaining conditions excluded
- Given a rule with only RULED_OUT conditions
- When `facts_used_by_rules(facts, rules)` is called
- Then returns empty set

## TC-03: No rules → empty set
- Given facts but no rules
- When `facts_used_by_rules(facts, rules)` is called
- Then returns empty set

## TC-04: Case-insensitive matching
- Given fact with noun="user", property="adminRole" and rule condition with noun="User", property="AdminRole"
- When `facts_used_by_rules(facts, rules)` is called
- Then the fact is included in the result

## TC-05: Same noun different property not matched
- Given fact (Error, code) and rule condition (Error, message)
- When `facts_used_by_rules(facts, rules)` is called
- Then the fact is NOT included
