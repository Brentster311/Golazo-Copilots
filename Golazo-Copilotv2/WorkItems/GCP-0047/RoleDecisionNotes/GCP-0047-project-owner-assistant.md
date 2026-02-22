# GCP-0047: Project Owner Assistant Decision Notes

## Scope Decisions

### Single Work Item vs. Multiple
The 8 changes touch overlapping role files — splitting them would create merge conflicts and require re-reading the same files repeatedly. Keeping as one work item because:
- All changes are to role markdown files only (no production code)
- Changes are interdependent (e.g., moving design-quality bullets from QA to Architect affects both files simultaneously)
- No behavior/scope ambiguity — PO explicitly approved each item

### Key Assumptions Made
1. **POA re-entry is a real transition** — transitions.py will be modified to add retrospective → project-owner-assistant as a forward transition. The POA role file gets a new "Closure" section that handles final commit, AC validation, and pending work item disposition. This requires code changes + tests.
2. **QA sharpening** — "Design quality" bullets move to Architect, but QA retains Review-Comments.md output because test critique still belongs there (and Architect already appends an "Architect Notes" section to the same file).
3. **Capability registry consolidation** — Removing from Domain Expert and QA only. Developer and Refactor Expert keep their checks (pre-commit and post-refactor). Architect keeps impact analysis, Builder keeps validation.

### Out of Scope Justification
- No new roles: Security Reviewer was option B; PO chose option A (expand Architect).
- No removal or reordering of existing roles in ROLE_ORDER — the POA re-entry is an additional forward transition, not a position change.
