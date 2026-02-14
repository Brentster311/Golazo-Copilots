# EES-00015 Design Doc: Highlight Rule-Used Facts

## Summary
Add visual highlighting (bold) to facts in the Proposed Facts table that are consumed by at least one proposed rule condition, plus a "Confirm Used" button to confirm just those facts.

## Problem Statement
After extraction, the user sees 10-15 proposed facts but only 4-5 are actually used by rules. There's no visual distinction, forcing the user to cross-reference facts and rule conditions manually.

## Business Case
Reduces review time per incident from minutes to seconds. Directly addresses user feedback that the fact/rule relationship is unclear.

## Stakeholders
- Knowledge engineer (primary user)

## Functional Requirements
1. Compute set of (noun, property) pairs from all proposed rule condition items (excluding chaining nouns)
2. Tag matching facts in the Treeview with a bold font
3. "Confirm Used" button confirms only the bold/used facts
4. Tooltip on the new button

## Non-Functional Requirements
- No perceptible lag on tables with up to 50 facts

## Proposed Approach
1. New adapter function `facts_used_by_rules(facts, rules)` returns the set of fact indices that are used
2. After populating the facts Treeview, apply a "used" tag with bold font to matching rows
3. New button calls `_confirm_used_facts()` which iterates the used set

## Alternatives Considered
- Color background instead of bold — harder to see on high-DPI, bold is universal
- Auto-confirm used facts — removes user agency

## Risks & Mitigations
- Risk: Font tag not rendering on all ttk themes → Mitigate: use `tkfont.Font` with bold weight
- Risk: Edge case where no facts are used → Button is a no-op, acceptable

## Dependencies
None — purely additive to existing GUI code.

## Test Strategy
- Unit test `facts_used_by_rules()` in `test_adapters.py`
- Manual GUI verification for bold rendering
