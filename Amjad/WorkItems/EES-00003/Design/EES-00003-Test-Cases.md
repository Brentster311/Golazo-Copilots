# EES-00003 — Test Cases

## Mapping: Acceptance Criteria → Test Cases

### AC-1: System proposes RULEOUT rules from incident text
| # | Test Case | Expected Outcome | Type |
|---|-----------|-------------------|------|
| 1 | `_parse_response` receives rules with `type: "ruleout"` and `then.noun: "RULEOUT"` | Returns `Rule` objects with `type="ruleout"`, `then.noun="RULEOUT"`, `then.value=<RC name>` | Unit |
| 2 | `_parse_response` receives rules without `type` field | Defaults to `type="positive"` (backward compat) | Unit |
| 3 | `_parse_response` receives mixed positive + RULEOUT rules | Both types parsed correctly in single response | Unit |

### AC-2: User can confirm, edit, or reject RULEOUT rules
| # | Test Case | Expected Outcome | Type |
|---|-----------|-------------------|------|
| 4 | `_confirm_rules` with RULEOUT rule, user confirms | Rule included in result | Unit |
| 5 | `_confirm_rules` with RULEOUT rule, user edits BECAUSE | BECAUSE updated, rule included | Unit |
| 6 | `_confirm_rules` with RULEOUT rule, user rejects | Rule excluded from result | Unit |

### AC-3: RULEOUT rules persisted with correct format
| # | Test Case | Expected Outcome | Type |
|---|-----------|-------------------|------|
| 7 | `Rule(type="ruleout").to_dict()` | Dict has `type: "ruleout"`, `then.noun: "RULEOUT"` | Unit |
| 8 | `Rule.from_dict()` with `type: "ruleout"` | Reconstructs Rule with correct type | Unit |
| 9 | `Rule.from_dict()` without `type` key | Defaults to `type="positive"` | Unit |
| 10 | Save and reload RULEOUT rule via `YamlStore` | Round-trip preserves type and all fields | Unit |

### AC-4: RULEOUT rules carry status, sources, BECAUSE
| # | Test Case | Expected Outcome | Type |
|---|-----------|-------------------|------|
| 11 | RULEOUT rule with status=CONFIRMED, sources=[INC-001], because="..." | All fields serialize/deserialize correctly | Unit |
| 12 | RULEOUT rule with status=GAP | Valid combination — serializes correctly | Unit |

### AC-5: RULEOUT rules distinguishable from positive rules
| # | Test Case | Expected Outcome | Type |
|---|-----------|-------------------|------|
| 13 | `list_rules()` returns mix of positive and ruleout rules | Can filter by `rule.type` to distinguish | Unit |
| 14 | Display format in `_confirm_rules` for ruleout rule | Shows `THEN RULEOUT <name>` not `THEN RULEOUT(*).Target = <name>` | Unit |

### AC-6: rootcauses.yaml not modified by RULEOUT rules
| # | Test Case | Expected Outcome | Type |
|---|-----------|-------------------|------|
| 15 | Process incident with RULEOUT rules but no positive root cause confirmation | rootcauses.yaml unchanged | Integration |
| 16 | Process incident with both positive root cause + RULEOUT rules | rootcauses.yaml only updated for the positive root cause | Integration |

### Cross-cutting: Deduplication
| # | Test Case | Expected Outcome | Type |
|---|-----------|-------------------|------|
| 17 | `is_duplicate` with RULEOUT rule matching existing RULEOUT rule | Returns True (exact dup) | Unit |
| 18 | `is_duplicate` with RULEOUT rule vs existing positive rule (different then) | Returns False (not duplicate) | Unit |
| 19 | `filter_rules` with RULEOUT rule whose conditions are all confirmed | Rule passes filter | Unit |

### Cross-cutting: GAP Detection Interaction
| # | Test Case | Expected Outcome | Type |
|---|-----------|-------------------|------|
| 20 | `detect_gaps` with facts connected only via RULEOUT rules | Facts are considered connected, no GAP created | Unit |
| 21 | `detect_gaps` with facts connected via mix of positive + RULEOUT rules | All connected facts excluded from orphan set | Unit |
| 22 | `detect_gaps` with RULEOUT rules present but facts still orphaned | GAP rule created for orphaned facts | Unit |

### Integration: Full Workflow
| # | Test Case | Expected Outcome | Type |
|---|-----------|-------------------|------|
| 23 | `process_incident` with LLM returning RULEOUT rules | RULEOUT rules confirmed, persisted with type="ruleout" | Integration |
| 24 | `process_incident` summary includes RULEOUT count | Output shows `N positive, M ruleout generated` | Integration |
| 25 | `process_incident` with only RULEOUT rules (no positive) | RULEOUT rules saved, rootcauses.yaml unchanged, summary correct | Integration |

**Total: 25 test cases across 6 acceptance criteria + 2 cross-cutting areas.**
