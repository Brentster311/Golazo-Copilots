# GCP-0077 Project Owner Assistant Notes

## Scope Decision

Remove the three Azure Identity dependency probes from the default test suite. They test an optional third-party package that Golazo Copilot does not install and therefore produce expected skips rather than continuous product assurance.

## Constraints

- Preserve the packaged Azure guidance.
- Preserve static checks for the best-practices document.
- Do not change package versions or dependencies.
- Push the completed change directly to `main` as explicitly requested.

## Capability Impact

`golazo_capabilities impact` reported no registered capabilities affected by `golazo-copilot/tests/test_best_practices.py`.