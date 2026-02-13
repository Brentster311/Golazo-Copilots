# EES-00003 — Refactor Expert Decision Notes

## Refactoring Applied

### RF-1: Extracted `_format_rule_then()` helper
- **Problem:** RULEOUT then-clause formatting was duplicated in `_confirm_rules` display and summary output (2 identical if/else blocks).
- **Solution:** Extracted `_format_rule_then(rule: Rule) -> str` alongside existing `_format_rule_conditions()`.
- **Benefit:** Single source of truth for then-clause display. Future rule types only need one change.
- **Behavior change:** None.

## No Other Refactoring Needed
The EES-00003 changes were minimal and well-structured:
- Model: 1-line Literal expansion
- Fact extractor: 1-line type read + prompt text
- Gap detector: 4-line broadening
- No code smells detected in the new code.

## Test Verification
159 tests pass before and after refactoring. No behavior changes.
