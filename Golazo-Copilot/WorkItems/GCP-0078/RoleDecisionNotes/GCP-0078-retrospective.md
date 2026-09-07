# GCP-0078 Retrospective

## What Went Well

- The truth audit was converted into source-backed contract tests before documentation changes.
- Red-green validation caught all six original gaps and a residual broad force claim.
- Capability impact and validation were consulted at POA, Developer, and Builder stages.
- Full functional, coverage, lint, package-build, and release-policy checks passed.

## What Did Not Go Well

- Express sends work directly to QA, but QA requires a Program Manager design document even though Program Manager is not in that profile.
- The initial story prohibited a version change despite mandatory Builder release policy, causing a backward workflow pass.
- Coverage tracing invalidates the strict `<10 ms` performance test, so a single full coverage command cannot pass reliably.
- One execution helper reported a wheel from the wrong context; direct terminal verification was required.

## Action Items

- Create a follow-up work item to align Express QA entry conditions with the profile's available roles.
- Decide whether to expose a supported role-note bypass or remove the ineffective `skip_role` consent path.
- Separate strict timing tests from coverage-instrumented suite commands in documented build guidance.
- Align Builder push guidance with the `<useralias>/<workitem-id>` branch format.
- Add a release-policy checklist to POA scoping so version expectations do not conflict with Builder requirements.

## Metrics

- Zero profile roles requiring artifacts owned only by excluded roles.
- Zero documented consent actions without a callable consuming operation.
- One standard validation command set that passes consistently with coverage and timing checks separated.
- Zero branch-name mismatches across packaged role instructions.