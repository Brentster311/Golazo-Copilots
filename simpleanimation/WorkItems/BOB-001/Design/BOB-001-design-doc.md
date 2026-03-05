# BOB-001 — Design Doc: Bob Stick Figure Animation

## Summary
A single-file Python script using pygame that animates a stick figure named Bob through three phases: sitting → standing up → flying a kite. The animation loops continuously.

## Problem Statement
The user wants a fun, simple animated stick figure app. No existing asset exists — just a hand-drawn reference image of a stick figure.

## Business Case
- **Why now**: User request — creative/fun project.
- **Impact**: Demonstrates simple procedural animation in Python.
- **KPIs**: App runs, animation looks correct, user is satisfied.

## Stakeholders
- User (requestor and sole audience)

## Functional Requirements
1. Draw Bob as a stick figure (circle head, line body, arms, legs)
2. Phase 1 — **Sitting** (~2s): Bob shown seated (legs bent, body leaning)
3. Phase 2 — **Standing up** (~2s): Bob transitions from sitting to standing (legs straighten, torso rises)
4. Phase 3 — **Flying a kite** (~4s): Bob stands holding a string; a diamond-shaped kite sways in the sky
5. Loop back to Phase 1

## Non-Functional Requirements
- 60 FPS rendering
- Window size: 600×500 pixels
- Smooth interpolation between poses (linear lerp)
- Clean exit on window close

## Proposed Approach
- Single Python file `bob_animation.py`
- Use pygame for window, drawing, and game loop
- Define Bob's pose as a set of joint positions (head, shoulders, hips, knees, feet, hands)
- Define keyframe poses for sitting, standing, kite-flying
- Interpolate between keyframes over time
- Draw kite as a diamond shape with a tail, connected to Bob's hand by a line
- Kite sways using sine wave offset

## Alternatives Considered
| Option | Pros | Cons |
|--------|------|------|
| tkinter Canvas | No install needed | Choppy animation, no double buffering |
| matplotlib animation | Good for math viz | Overkill, slow for real-time |
| **pygame (chosen)** | Smooth, simple API | Requires pip install |

## Risks & Mitigations
| Risk | Mitigation |
|------|-----------|
| pygame not installed | Script prints install instructions if import fails |
| Animation looks jerky | Use delta-time based interpolation, not frame-counting |

## Dependencies
- Python 3.8+
- pygame (`pip install pygame`)

## Migration / Rollout / Rollback
- N/A — single script, no deployment

## Observability
- N/A — desktop app with no logging needed

## Test Strategy
- Manual: run script, visually confirm three animation phases
- Verify window closes cleanly
- Verify animation loops
