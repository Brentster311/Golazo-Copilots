# EES-00002 — Quality Assurance Decision Notes

**Role:** quality-assurance  
**Work Item:** EES-00002 — GAP Rule Detection & Refinement  
**Date:** 2025-02-01

## Review Approach

Reviewed the design doc (`EES-00002-design-doc.md`) against the user story's 5 acceptance criteria, the master decisions in `docs/expert-system-decisions.md`, and the existing codebase (models, yaml_store, main.py orchestration).

## Key Findings Summary

### Major Findings (3)
1. **MJ-1**: "Orphaned facts" definition needs precise algorithm — design says facts not connected to root cause through existing rules, but doesn't specify traversal depth or matching semantics.
2. **MJ-2**: Behavior when no root cause is confirmed is unspecified. Recommended: skip GAP detection entirely (no root cause = nothing to bridge toward).
3. **MJ-3**: GAP refinement matching is underspecified — how does a new CONFIRMED rule "overlap" with a GAP's requires/produces? Exact match? Subset? Fact.match_key()?

### Minor Findings (3)
1. **MN-1**: requires/produces fields on Rule model (vs separate GapRule class) — accepted as reasonable tradeoff for simplicity.
2. **MN-2**: RESOLVED status not in acceptance criteria but in design — acceptable extension.
3. **MN-3**: Should `filter_rules()` exclude GAP rules from dedup comparison? Deferred to architect.

## Questions for Architect

1. Define the exact algorithm for detecting "orphaned facts" — single-hop? Multi-hop chain? Graph traversal?
2. When no root cause exists, should GAP detection be skipped entirely?
3. How should refinement matching work — by `Fact.match_key()` comparison between GAP requires and new rule conditions?
4. Should `filter_rules()` skip GAP-status rules when checking for duplicates?

## Test Strategy

- 28 test cases created across 7 categories
- All 5 acceptance criteria mapped
- Edge cases cover backward compatibility with pre-GAP YAML files
- TC-28 deferred pending architect decision on MN-3
- Tests are deterministic (no LLM calls in GAP detection)

## Decision

Design is **conditionally approved** pending architect resolution of MJ-1, MJ-2, MJ-3, and MN-3.
