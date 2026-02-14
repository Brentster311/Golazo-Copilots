# EES-00015 — Project Owner Assistant Notes

## Decisions
- Single user story: the bold highlighting and "Confirm Used" button are a single user-observable outcome (see used facts, act on them).
- "Used" defined by condition (noun, property) match, excluding chaining nouns — consistent with existing `_handle_submit_rule` fact-constraint validation.
- Interface, platform, persistence, user type all established from prior work items (Tkinter GUI, Windows, file-based, technical user).

## Scope Justification
Small, shippable feature: one adapter function + two GUI changes (tag styling + button). No model or persistence changes needed.
