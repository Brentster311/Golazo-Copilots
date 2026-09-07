# GCP-0074 Capability Impact

## Registry Result

The registry reports `bootstrap-skill-installation` as directly affected because packaged bootstrap instructions are among the documentation surfaces reviewed for consistency.

## Direct Impact

- `bootstrap-skill-installation`: documentation wording may change, but installation behavior, inputs, outputs, consent rules, and file-copy contracts are unchanged.

## Transitive Impact

None identified.

## Contract Implications

- `golazo_transition_workitem` changes its eligibility contract from current role Retrospective to completed POA closure.
- Tool name, input schema shape, result shape, next-ID computation, and global-state schema remain unchanged.
- Invalid lifecycle or evidence returns structured, actionable failures before mutation.

## Compatibility

No state migration or dependency change is required. Existing closed work items become finalizable; premature Retrospective calls are intentionally rejected to preserve mandatory POA acceptance.
