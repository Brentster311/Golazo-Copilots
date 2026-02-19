# EES-00018: Goal Declaration and Evaluation Termination

**Status**: IMPLEMENTED

**User Story**

- **Title**: Add explicit goal declaration to incidents so the rule engine knows when to stop
- **As a**: knowledge engineer running the evaluation engine against an incident
- **I want**: each evaluation session to declare a **goal** (a typed fact that starts at an initial value and must reach a terminal value), with **resolution rules** that assign root causes and a **termination condition** that stops evaluation when the goal is satisfied
- **So that**: the engine doesn't just rule things out endlessly — it converges toward an answer, and both the operator and the system know whether the problem was solved or escalated

- **Out of scope**:
  - Automatic goal inference from incident text (goals are declared by the ontology or the user)
  - GUI goal editor (the goal is set in the incident YAML or evaluation config — GUI display is a follow-up)
  - Changing rule authoring UX (resolution rules are authored the same way as diagnostic rules)
  - Multi-goal evaluation (one goal per session)

- **Assumptions**:
  - **Assumption (explicit)**: Depends on EES-00016 (typed ontology) and EES-00017 (structured CHANGE_STATE). Resolution rules use structured targets to write to the goal property.
  - **Assumption (explicit)**: A "goal" is an `OntologyProperty` on a goal noun (e.g., `Incident($inc).rootCause`) with an `initial` value and a set of `terminal` values. Evaluation terminates when the goal fact's value is in the terminal set.
  - **Assumption (explicit)**: Two termination outcomes exist: **resolved** (goal reached a known terminal value like `admin_role_missing`) and **escalated** (a GAP rule fired, meaning all known causes were eliminated). Both are terminal.
  - **Assumption (explicit)**: The goal declaration is stored in the ontology YAML as a special property annotation, not in the incident file. This makes goals reusable across incidents of the same type.

- **Acceptance Criteria (bulleted, testable)**:
  - `OntologyProperty` supports optional `is_goal: bool`, `initial: str`, and `terminal: list[str]` fields for goal properties
  - `EvaluationResult` has a new field `goal_status: Literal["in_progress", "resolved", "escalated"]` computed from the goal fact's final value
  - The rule evaluator's main loop checks the goal fact after each rule fires; if the goal fact's value is in the terminal set, evaluation stops immediately and `goal_status = "resolved"`
  - If a GAP rule fires and the goal is still `in_progress`, `goal_status = "escalated"` and evaluation stops
  - If max iterations are reached without resolution or escalation, `goal_status = "in_progress"` (inconclusive)
  - Resolution rules (rules whose CHANGE_STATE target is the goal property) can be authored and serialized using the same `Rule` model
  - Unit tests cover: goal-based termination on resolution, goal-based termination on escalation, max-iteration fallback, evaluation without a goal (backward compat — behaves as today)

- **Non-functional requirements**: No new dependencies; backward compatible (evaluations without a goal defined work exactly as before)
- **Telemetry / metrics expected**: N/A
- **Rollout / rollback notes**: Additive fields. Existing ontology/incident YAML loads cleanly without goals. Goal-based termination only activates when a goal property is declared.
