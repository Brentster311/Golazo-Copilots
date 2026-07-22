# GCP-0071 Architect Notes

## Architectural decision
- Preserve the existing closure model and generalize the retro-to-POA entry path to all profiles.

## Rationale
- This is the smallest coherent fix because POA closure artifacts, closure-only output gating, and status formatting already exist.
- Changing the terminal profile behavior is lower risk than inventing a separate closure mechanism for express and spike.

## Review emphasis for implementation
- Update both transition validation and closure-mode entry logic.
- Keep all non-closure profile sequencing unchanged.
- Align bootstrap and role instruction sources with the runtime behavior.