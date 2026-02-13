# EES-00005 — Test Cases

## Mapping: Acceptance Criteria → Test Cases

### AC-1: Load incident via file browser dialog
| # | Test Case | Expected Outcome | Type |
|---|-----------|-------------------|------|
| 1 | Load valid .txt file | Incident text displayed in read-only text area | Manual |
| 2 | Load non-existent file path | Error dialog shown, no crash | Manual |
| 3 | Cancel file dialog | No action taken, UI unchanged | Manual |

### AC-2: AI-proposed facts displayed and reviewable
| # | Test Case | Expected Outcome | Type |
|---|-----------|-------------------|------|
| 4 | Facts returned from LLM displayed in table | Rows match LLM response facts with correct columns | Unit (adapter) |
| 5 | Confirm fact changes status to confirmed (green) | Fact status = "confirmed" | Unit (adapter) |
| 6 | Reject fact changes status to rejected (red) | Fact status = "rejected" | Unit (adapter) |
| 7 | Edit fact via dialog updates fact values | Updated fact reflects new values | Manual |

### AC-3: Generated rules displayed after fact confirmation
| # | Test Case | Expected Outcome | Type |
|---|-----------|-------------------|------|
| 8 | Rules displayed with IF/THEN/BECAUSE format | Conditions, then clause, and because visible | Unit (adapter) |
| 9 | RULEOUT rules shown with visual distinction | RULEOUT label visible, different styling/icon | Manual |

### AC-4: Ontology browsable in tree/list view
| # | Test Case | Expected Outcome | Type |
|---|-----------|-------------------|------|
| 10 | Ontology tree shows nouns with properties | Tree structure: noun → property nodes | Unit (adapter) |
| 11 | Empty ontology shows empty tree | No crash, empty display | Unit (adapter) |

### AC-5: Rule base browsable with filtering
| # | Test Case | Expected Outcome | Type |
|---|-----------|-------------------|------|
| 12 | All rules loaded and displayed | Rule count matches YAML files | Unit (adapter) |
| 13 | Filter by status=GAP shows only GAP rules | Filtered list contains only GAP status rules | Unit (adapter) |
| 14 | Filter by type=ruleout shows only RULEOUT rules | Filtered list contains only ruleout type rules | Unit (adapter) |
| 15 | Click rule expands details | Full rule details visible (conditions, then, because, sources) | Manual |

### AC-6: Run evaluation and view results
| # | Test Case | Expected Outcome | Type |
|---|-----------|-------------------|------|
| 16 | Evaluate with matching facts | Root causes shown in results panel | Unit (adapter) |
| 17 | Evaluate with RULEOUT match | Ruled-out causes shown | Unit (adapter) |
| 18 | Evaluate with GAP match | GAP rules listed in results | Unit (adapter) |
| 19 | Evaluate with no matching rules | Empty results displayed (no crash) | Unit (adapter) |

### AC-7: Changes persisted to YAML files
| # | Test Case | Expected Outcome | Type |
|---|-----------|-------------------|------|
| 20 | Process incident via GUI saves YAML files | incident.yaml, rules/*.yaml created | Integration |
| 21 | CLI can read files saved by GUI | `ees evaluate` works on GUI-saved data | Integration |

### Cross-cutting: Non-functional
| # | Test Case | Expected Outcome | Type |
|---|-----------|-------------------|------|
| 22 | LLM call doesn't freeze UI | Progress indicator visible, UI responsive | Manual |
| 23 | LLM call error shows dialog | Error message displayed, UI recoverable | Unit (worker) |
| 24 | Worker thread reports results correctly | Result queue/callback delivers data to UI thread | Unit (worker) |

**Total: 24 test cases across 7 ACs + 1 cross-cutting area.**

## Test Type Distribution
- **Unit (adapter/worker):** 14 tests — testable without Tk event loop
- **Integration:** 2 tests — engine round-trip through GUI adapter
- **Manual:** 8 tests — visual/interaction verification
