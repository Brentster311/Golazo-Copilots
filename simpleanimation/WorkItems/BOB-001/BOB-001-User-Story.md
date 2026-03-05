# BOB-001 — Bob Sits, Stands, Flies a Kite

**Status**: IN PROGRESS

**User Story**
- **Title**: Animate stick figure Bob sitting → standing → flying a kite
- **As a**: User
- **I want**: A simple Python desktop app that animates a stick figure named Bob who starts seated, stands up, and then flies a kite
- **So that**: I can see a fun looping stick-figure animation
- **Out of scope**: Sound effects, user controls (pause/rewind), saving/exporting video, multiple characters
- **Assumptions**:
  - **Assumption (explicit)**: pygame is used for rendering and animation (user confirmed)
  - **Assumption (explicit)**: Windows-only target (user confirmed)
  - **Assumption (explicit)**: The animation loops continuously
  - **Assumption (explicit)**: Stick figure is drawn procedurally (lines + circle), not from the provided image file
  - **Assumption (explicit)**: "Flying a kite" means Bob holds a string attached to a kite shape that sways in the sky
- **Acceptance Criteria (bulleted, testable)**:
  - [ ] App opens a pygame window displaying Bob as a stick figure in a sitting pose
  - [ ] Bob animates from sitting to standing over ~2 seconds
  - [ ] After standing, a kite appears and Bob holds a string connected to it
  - [ ] The kite sways/moves in the sky in a natural-looking way
  - [ ] The animation loops back to sitting after the kite-flying phase
  - [ ] Window can be closed via the X button
- **Non-functional requirements**: Runs at 60 FPS, window size ~600×500
- **Telemetry / metrics expected**: None
- **Rollout / rollback notes**: Single-file script, no deployment pipeline needed
