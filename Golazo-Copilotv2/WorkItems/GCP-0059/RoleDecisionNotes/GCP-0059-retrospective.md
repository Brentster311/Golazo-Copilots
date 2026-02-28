# GCP-0059 — Retrospective

## What went well
- Rapid convergence on terminology (`orchestrator-only`) improved clarity and reduced ambiguity.
- Role-gated artifact flow provided clear checkpoints before implementation.
- Capability impact + validate checks were useful and lightweight.
- Targeted regression tests gave fast confidence on behavior changes.

## What didn't go well
- Initial direction shifted from fallback messaging to required bootstrap, causing artifact rework.
- Terminal working-directory persistence caused repeated noisy `cd` warnings.
- Async test execution initially used the wrong interpreter, creating false failures.

## Action items
1. Add a concise decision log section early in PM docs to capture naming/policy pivots.
2. Standardize builder command templates to avoid duplicate `cd` path segments.
3. Add a test-run guideline to always invoke project `.venv` explicitly in automation notes.

## Metrics
- Rework count due requirement pivots: 1 significant pivot.
- Targeted regression pass rate after final implementation: 67/67.
- Capability registry validation failures: 0.
