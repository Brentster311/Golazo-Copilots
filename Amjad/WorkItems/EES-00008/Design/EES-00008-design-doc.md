# EES-00008 Design Document — Fact Scope Classification

## Summary
Add a `scope` field to the `Fact` dataclass (`"rule"` or `"context"`) and tighten the LLM system prompt to prevent extracting instance-specific identifiers. Together, these changes prevent overfit rules that match only a single incident.

## Problem Statement
When processing incident 586887556, the LLM extracted ~20 facts including resource group names, GUIDs, VMSS resource names, and activity IDs. These instance-specific values produce rules that never match any other incident. The system has no mechanism to distinguish generalizable facts (error codes, VM SKUs) from one-off identifiers.

## Business Case
- **Why now**: The system is entering live testing. Every overfit rule adds noise to the knowledge base, degrades evaluation accuracy, and requires manual cleanup.
- **Impact**: Without this, the knowledge base becomes polluted within the first 10–20 incidents processed. Rules that fire on GUIDs provide zero diagnostic value.
- **KPIs**: Reduction in rejected/useless rules per incident (target: >50% fewer instance-specific facts extracted).

## Stakeholders
- Support engineers (primary users)
- Project owner (Brent)

## Functional Requirements
1. `Fact` dataclass gains a `scope` field: `"rule"` (default) or `"context"`
2. LLM system prompt explicitly forbids extracting GUIDs, resource names, subscription IDs, region names
3. LLM JSON output includes `"scope"` per fact; parser reads it with fallback to `"rule"`
4. GUI Proposed Facts table shows Scope column with toggle capability (click to switch rule↔context)
5. `RuleGenerator.filter_rules()` only uses `scope == "rule"` facts for condition matching
6. `_save_all` passes only `rule`-scoped confirmed facts to `RuleGenerator`, but saves all facts on the Incident record
7. Existing YAML files without `scope` load with default `"rule"` — full backward compatibility

## Non-Functional Requirements
- No new dependencies
- Backward-compatible YAML schema
- No performance impact on evaluation

## Proposed Approach

### Layer 1: Prompt tuning (Option C)
Add explicit guidance to `_SYSTEM_PROMPT` in `fact_extractor.py`:
- Classify each fact as `"scope": "rule"` or `"scope": "context"`
- DO NOT extract: GUIDs, resource names, subscription IDs, correlation IDs, cluster/node/stamp names
- DO extract: error codes, VM SKUs, operation types, failure categories, boolean states

### Layer 2: Scope field (Option A)
- Add `scope: Literal["rule", "context"] = "rule"` to `Fact` dataclass
- Update `to_dict()`, `from_dict()`, `to_condition_dict()` for serialization
- Update `_parse_response()` in `FactExtractor` to read scope from LLM output
- Update `facts_to_rows()` adapter to include scope
- Update GUI: add Scope column to facts_tree, add toggle button
- Update `_save_all()`: filter confirmed facts by scope before passing to RuleGenerator
- Update `RuleGenerator`: no changes needed if caller filters correctly

## Alternatives Considered
See Project Owner Assistant decision notes — Options B (ontology classification) and D (regex heuristics) were evaluated and deferred/rejected.

## Risks & Mitigations
| Risk | Mitigation |
|------|-----------|
| LLM ignores scope instructions | User can manually toggle scope in GUI before saving |
| LLM classifies a generalizable fact as "context" | User override + default-to-rule fallback |
| Existing tests depend on Fact field count | Update test fixtures to include scope field |

## Open Questions
None — design is straightforward.

## Dependencies
- Existing `Fact` dataclass (models.py)
- Existing `FactExtractor._parse_response` (fact_extractor.py)
- Existing GUI facts table (app.py)

## Migration / Rollout / Rollback
- **Migration**: None needed. `scope` defaults to `"rule"`, so old YAML loads unchanged.
- **Rollout**: Immediate on next app launch.
- **Rollback**: Revert commit; old code ignores the `scope` field in YAML files.

## Observability Plan
- N/A (desktop application, no telemetry)

## Test Strategy Summary
- Unit tests: Fact serialization round-trip with scope, Fact.from_dict without scope (backward compat)
- Unit tests: FactExtractor._parse_response with scope in JSON, without scope in JSON
- Unit tests: facts_to_rows includes scope column
- Unit tests: _save_all filters by scope before rule generation
- Integration: Extract facts from sample incident, verify scope classification
