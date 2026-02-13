# EES-00002 — Refactor Expert Decision Notes

**Role:** refactor-expert  
**Work Item:** EES-00002 — GAP Rule Detection & Refinement  
**Date:** 2025-02-01

## Findings (2)

| # | Finding | Action |
|---|---------|--------|
| RF-1 | Duplicated status-free fact serialization in 3 places (RuleConditions.to_dict, Rule.to_dict requires/produces) | Extracted `Fact.to_condition_dict()` |
| RF-2 | Repeated `tuple[str, str, str, str, str]` type annotation in gap_detector.py | Added `MatchKey` type alias |

## Changes Applied

### RF-1: `Fact.to_condition_dict()`
- New method returns `{noun, instance, property, operator, value}` without status
- `Fact.to_dict()` now delegates to `to_condition_dict()` and adds status
- `RuleConditions.to_dict()` uses `[f.to_condition_dict() for f in self.items]`
- `Rule.to_dict()` requires/produces uses `[f.to_condition_dict() for f in ...]`
- Eliminates 3 instances of manual dict construction

### RF-2: `MatchKey` type alias
- `MatchKey = tuple[str, str, str, str, str]` in gap_detector.py
- Applied to `connected_keys` and `new_condition_keys` annotations

## Verification

- 140 tests passed, 0 failed
- No behavior change
