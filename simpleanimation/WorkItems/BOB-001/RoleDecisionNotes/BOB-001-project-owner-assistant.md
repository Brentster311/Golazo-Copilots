# BOB-001 — Project Owner Assistant Decision Notes

## Decisions Made
1. **Interface**: Desktop GUI window (pygame) — confirmed by user
2. **Platform**: Windows only — confirmed by user
3. **Library**: pygame — confirmed by user (smooth animation, pip install required)
4. **Data persistence**: None needed — animation is entirely in-memory
5. **User type**: End user — no technical knowledge required beyond running a Python script

## Scope Rationale
Single user story — one user-observable outcome (the animation). No decomposition needed.

## Assumptions Justification
- Procedural drawing chosen because the provided image is a hand-drawn reference, not an asset to embed.
- Looping animation assumed because no explicit end-state was described.
- Kite behavior inferred as a swaying kite on a string — the most natural interpretation of "flying a kite."
