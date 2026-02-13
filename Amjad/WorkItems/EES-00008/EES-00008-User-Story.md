# EES-00008: Fact Scope Classification — Prevent Rule Overfitting

**Status**: BACKLOG

## User Story
- **Title**: Fact scope classification to prevent rule overfitting
- **As a**: Support engineer using the EES GUI
- **I want**: Extracted facts to be classified as either "rule" (generalizable) or "context" (instance-specific), with the LLM avoiding instance-specific extractions and the GUI letting me override scope before saving
- **So that**: Rules are built only from generalizable facts (error codes, VM SKUs, failure categories) and not from one-off identifiers (resource group names, GUIDs, specific cluster names) that would never match another incident

- **Out of scope**:
  - Ontology-level property classification (Option B — deferred to future work item when ontology is mature)
  - Regex-based heuristic filtering (Option D — prompt + user override is sufficient)
  - Changes to the Evaluate tab or rule evaluation logic (rules already only use their stored conditions)

- **Assumptions**:
  - **Assumption (explicit)**: The existing `status` field ("confirmed"/"rejected") remains orthogonal to `scope` — a fact can be `rule + confirmed`, `context + confirmed`, or `rejected`. Rejected facts are excluded from everything regardless of scope.
  - **Assumption (explicit)**: The LLM prompt change (Option C) and the scope field (Option A) ship together as one deliverable since they address the same problem from two angles.
  - **Assumption (explicit)**: `scope` defaults to `"rule"` for backward compatibility with existing saved incidents that lack the field.

- **Acceptance Criteria (bulleted, testable)**:
  - [ ] `Fact` dataclass has a `scope` field with values `"rule"` or `"context"`, defaulting to `"rule"`
  - [ ] LLM system prompt instructs the model to classify each fact's scope AND explicitly forbids extracting GUIDs, resource names, subscription IDs, and region names (unless root cause is region-specific)
  - [ ] `_parse_response` in `FactExtractor` reads the `scope` field from LLM JSON output, falling back to `"rule"` if absent
  - [ ] GUI Proposed Facts table displays a "Scope" column; user can toggle between `rule`/`context` per-fact before saving
  - [ ] `RuleGenerator.filter_rules()` only considers facts with `scope == "rule"` when matching conditions
  - [ ] `_save_all` in the GUI excludes `context`-scoped facts from the confirmed facts passed to `RuleGenerator`, while still saving all facts (both scopes) on the `Incident` record
  - [ ] Existing YAML incidents without `scope` load correctly with `scope` defaulting to `"rule"`

- **Non-functional requirements**:
  - No new dependencies
  - Backward-compatible with existing YAML data files

- **Telemetry / metrics expected**:
  - N/A (local desktop app)

- **Rollout / rollback notes**:
  - Existing saved incidents will auto-default `scope="rule"` on load — no migration needed
  - LLM prompt change takes effect immediately on next extraction
