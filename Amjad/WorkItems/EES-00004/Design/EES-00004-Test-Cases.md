# EES-00004 — Test Cases

## Mapping: Acceptance Criteria → Test Cases

### AC-1: Evaluates rules and reports matching root causes
| # | Test Case | Expected Outcome | Type |
|---|-----------|-------------------|------|
| 1 | Single rule fires: IF CPUUsage > 90 THEN RootCause = X | `root_causes` contains "X" | Unit |
| 2 | No rules fire (no matching conditions) | `root_causes` is empty, `fired_rules` is empty | Unit |
| 3 | Multiple root causes identified | Both appear in `root_causes` | Unit |

### AC-2: Reports RULEOUT rules and eliminated root causes
| # | Test Case | Expected Outcome | Type |
|---|-----------|-------------------|------|
| 4 | RULEOUT rule fires | `ruled_out` contains eliminated root cause name | Unit |
| 5 | Both positive and RULEOUT rules fire | `root_causes` and `ruled_out` both populated | Unit |

### AC-3: Reports encountered GAP rules
| # | Test Case | Expected Outcome | Type |
|---|-----------|-------------------|------|
| 6 | GAP rule whose requires are all in working set | GAP appears in `gap_rules` | Unit |
| 7 | GAP rule whose requires are partially met | GAP does NOT appear in `gap_rules` | Unit |

### AC-4: Full rule chain trace (traceability)
| # | Test Case | Expected Outcome | Type |
|---|-----------|-------------------|------|
| 8 | Two-rule chain: A→B→RootCause | `rule_trace` has 2 entries in order | Unit |
| 9 | Trace entry contains rule_id and derived fact | Each trace dict has `rule_id` and `derived` keys | Unit |

### AC-5: Rules evaluated in dependency order (chaining)
| # | Test Case | Expected Outcome | Type |
|---|-----------|-------------------|------|
| 10 | Chain: IF X THEN Y, IF Y THEN RootCause=Z. Input: X | RootCause=Z is identified | Unit |
| 11 | Three-level chain: A→B→C→RootCause | All intermediates fire, root cause found | Unit |
| 12 | Convergence: rules that can't fire are skipped | Only applicable rules in `fired_rules` | Unit |

### AC-6: Conflicting root causes presented as candidates
| # | Test Case | Expected Outcome | Type |
|---|-----------|-------------------|------|
| 13 | Two rules assign different root causes from same facts | Both root causes in `root_causes` | Unit |

### AC-7: Structured output
| # | Test Case | Expected Outcome | Type |
|---|-----------|-------------------|------|
| 14 | `EvaluationResult.to_dict()` serialization | Contains all expected keys | Unit |
| 15 | Output written to file with `--output` | YAML file created with correct structure | Integration |

### Cross-cutting: CLI Integration
| # | Test Case | Expected Outcome | Type |
|---|-----------|-------------------|------|
| 16 | `ees evaluate --facts "..." --data-dir ...` | Runs evaluation, prints results | Integration |
| 17 | `ees evaluate --facts-file ... --data-dir ...` | Reads facts from file, evaluates | Integration |
| 18 | `--facts` with invalid fact format | Error reported, no crash | Integration |
| 19 | `--data-dir` with no rules | Reports 0 rules fired | Integration |

### Cross-cutting: Edge Cases
| # | Test Case | Expected Outcome | Type |
|---|-----------|-------------------|------|
| 20 | Empty input facts | No rules fire, empty result | Unit |
| 21 | Rule with OR logic fires when any condition matches | Rule fires correctly | Unit |
| 22 | Derived fact matches another rule (chaining via derived) | Chain works correctly | Unit |

**Total: 22 test cases across 7 ACs + 2 cross-cutting areas.**
