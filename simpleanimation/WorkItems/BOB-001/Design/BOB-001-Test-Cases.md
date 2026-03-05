# BOB-001 — Test Cases

## TC-01: App launches and displays window
- **Maps to AC**: App opens a pygame window displaying Bob
- **Steps**: Run `python bob_animation.py`
- **Expected**: A 600×500 window opens with a stick figure visible
- **Failure message**: "Window did not open or stick figure not visible"

## TC-02: Sitting pose displayed initially
- **Maps to AC**: Bob starts in a sitting pose
- **Steps**: Launch app, observe first frame
- **Expected**: Bob's legs are bent, body is in seated position
- **Failure message**: "Initial pose does not appear to be sitting"

## TC-03: Standing transition animates
- **Maps to AC**: Bob animates from sitting to standing over ~2 seconds
- **Steps**: Watch animation after launch
- **Expected**: Bob smoothly transitions from sitting to standing
- **Failure message**: "Standing transition is missing or jerky"

## TC-04: Kite appears after standing
- **Maps to AC**: A kite appears and Bob holds a string
- **Steps**: Watch animation after standing phase
- **Expected**: Diamond-shaped kite appears connected to Bob's hand by a line
- **Failure message**: "Kite or string not visible"

## TC-05: Kite sways naturally
- **Maps to AC**: Kite sways/moves in the sky
- **Steps**: Observe kite during flying phase
- **Expected**: Kite oscillates with natural-looking motion
- **Failure message**: "Kite is static or moves unnaturally"

## TC-06: Animation loops
- **Maps to AC**: Animation loops back to sitting
- **Steps**: Watch through full cycle
- **Expected**: After kite-flying, Bob returns to sitting pose and cycle repeats
- **Failure message**: "Animation does not loop"

## TC-07: Window closes cleanly
- **Maps to AC**: Window can be closed via X button
- **Steps**: Click the X button during animation
- **Expected**: Window closes, process exits without error
- **Failure message**: "Window did not close or process hung"
