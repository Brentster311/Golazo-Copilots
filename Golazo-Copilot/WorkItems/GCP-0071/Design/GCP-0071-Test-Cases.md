# GCP-0071 Test Cases

## Acceptance Criteria Mapping

### AC1: Transition validation allows retrospective -> project-owner-assistant for all profiles
- Test: Validate `retrospective -> project-owner-assistant` succeeds for `complete`, `express`, and `spike`.
- Expected result: Each profile returns `(True, None)` or equivalent success path.
- Failure message: `Expected profile <profile> to allow retrospective -> project-owner-assistant closure transition`.

### AC2: Closure mode activates for any profile when transitioning retrospective -> project-owner-assistant
- Test: Execute `golazo_transition` from retrospective to POA for express and spike fixture work items.
- Expected result: state enters `current_phase = "closure"` and `closure_pending = True`.
- Failure message: `Expected closure mode for profile <profile> when transitioning retrospective -> project-owner-assistant`.

### AC3: Instructions no longer say express/spike end at retrospective
- Test: Assert canonical bootstrap instructions and retrospective guidance contain universal POA closure wording.
- Expected result: no shipped instruction source claims express or spike end at retrospective.
- Failure message: `Expected instructions to route all profiles to project-owner-assistant closure after retrospective`.

### AC4: Complete-profile behavior remains intact
- Test: Re-run existing complete-profile closure tests alongside new express/spike coverage.
- Expected result: existing closure-mode assertions continue to pass without behavior regressions.
- Failure message: `Expected complete-profile closure behavior to remain unchanged while extending non-complete profiles`.