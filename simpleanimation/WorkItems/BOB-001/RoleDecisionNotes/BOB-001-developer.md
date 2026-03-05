# BOB-001 — Developer Decision Notes

## Implementation Decisions
1. **Single-file script**: `bob_animation.py` — no modules or packages needed.
2. **Keyframe-based animation**: Defined 3 poses (sitting, standing, kite-holding) as joint position dicts. Used linear interpolation with cubic ease-in-out for smooth transitions.
3. **6-phase animation cycle**: sit → stand up → raise arm → fly kite → lower arm → sit down (~12s total loop).
4. **Delta-time animation**: Used `clock.tick(FPS)` for frame timing, accumulated `dt` for phase tracking. Frame-rate independent.
5. **Visual polish**: Added clouds, ground, kite with tail segments, phase labels, and smooth fade in/out for the kite.
6. **Graceful import failure**: Try/except on pygame import with helpful error message.

## TDD Note
Test cases (BOB-001-Test-Cases.md) are all manual/visual for this graphical app. No automated test framework applies — verification is done by running the app and observing the animation phases.

## No Escalations
Implementation matches the design doc and user story exactly.
