# GCP-0048 — Developer Decision Notes

## Implementation Summary

### TDD Red Phase
- Created `tests/test_role_self_contained.py` with 64 test cases (8 test functions × 10 role files, minus 2 parametrized to 4 for TC-8)
- Red phase: 33 failed, 31 passed (expected — front-matter didn't exist yet)

### TDD Green Phase
- Added YAML front-matter to all 10 role files in `roles/defaults/`
- Fixed 3 implicit cross-role references:
  - `developer.md`: "DoR complete:" → "All definition-of-ready artifacts exist:" with explicit `WorkItems/{id}/` paths
  - `documenter.md`: "Implementation complete / Tests passing" → "All tests passing / Code changes committed / Developer notes exist"
  - `builder.md`: "Developer role complete / Refactor role complete" → explicit artifact path references
- Green phase: **357 passed, 0 failed** (64 new + 293 existing)

### Files Changed
- 10 role files in `golazo-copilot/src/golazo_copilot/roles/defaults/` (front-matter added)
- 3 of those files also had entry conditions updated (developer, documenter, builder)
- 1 new test file: `golazo-copilot/tests/test_role_self_contained.py`

### Design Decisions During Implementation
1. Front-matter `outputs:` for refactor-expert uses `{id}-refactor.md` (not `{id}-refactor-expert.md`) to match `ROLE_SUFFIX_MAP` in `gcp_transition.py`
2. TechBestPractices.md path kept as `.github/roles/TechBestPractices.md` (correct deployed path)
3. `inputs: []` used for project-owner-assistant (first role, no prior artifacts)
4. Retrospective `inputs:` lists all 9 prior role decision notes
5. AC2 regex test allows "Developer role complete" (explicit lookbehind exemption) since it's a named reference, not an implicit "role complete" pattern
