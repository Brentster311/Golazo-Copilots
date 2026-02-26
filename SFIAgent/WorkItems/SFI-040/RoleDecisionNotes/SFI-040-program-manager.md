# SFI-040 Program Manager Notes

## Scope
Single vertical slice: table presentation enhancement (column order + derived `Score/Min`).

## Why This Scope
The request is user-visible, additive, and self-contained in table rendering logic. It does not require new APIs or storage changes.

## Acceptance Mapping
- AC1/AC2: UI column order and new column existence.
- AC3/AC4: Correct formula and explicit zero-cost fallback (`28,800`) behavior.
- AC5: No persistence/data pipeline changes.

## Delivery Constraints
- Keep changes minimal and localized.
- Maintain existing table behavior outside requested adjustments.
