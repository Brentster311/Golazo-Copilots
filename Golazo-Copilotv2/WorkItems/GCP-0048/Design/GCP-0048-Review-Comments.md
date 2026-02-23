# GCP-0048 Review Comments

## Design Review

### Strengths
1. Clear front-matter format with well-defined schema (`inputs`, `outputs`, `tools`)
2. Comprehensive implicit reference replacement strategy with concrete before/after examples
3. Backward compatibility analysis is thorough — parser regex validated against source

### Issues Found

#### Issue 1: Front-matter may confuse `domain-expert.md` version detection (LOW)
The `<!-- Last Updated in Golazo Copilot Version: 2.104.5 -->` comment in `domain-expert.md` uses a different version than others (2.104.5 vs 2.102.0). Moving front-matter above it is fine but ensure the version comment remains for traceability.
- **Recommendation:** Keep the `<!-- Last Updated -->` comment right after the closing `---`. Update version to current when modifying.

#### Issue 2: `refactor-expert.md` Required Outputs says `{id}-refactor.md` (MEDIUM)
The front-matter `outputs:` must use `{id}-refactor.md` (not `{id}-refactor-expert.md`) to match `ROLE_SUFFIX_MAP` in `gcp_transition.py`. The design doc's front-matter table shows `{id}-refactor-expert.md` — **this is incorrect** and will cause AC6 drift test to fail.
- **Recommendation:** Use `WorkItems/{id}/RoleDecisionNotes/{id}-refactor.md` in both front-matter and Required Outputs (consistent with existing code).

#### Issue 3: `domain-expert.md` has conditional output (LOW)
Domain expert optionally writes to `Review-Comments.md` (when expertise IS needed) but the Required Outputs only lists the decision notes. The front-matter `outputs:` should match this — only `{id}-domain-expert.md` is required, `Review-Comments.md` is optional.
- **Recommendation:** Add comment in front-matter or separate `optional_outputs:` key. Or simply document in notes that Review-Comments is situational.

#### Issue 4: AC2 regex pattern list may be incomplete (MEDIUM)
Design lists: "previous role", "from the last", "earlier phase", "already created". Additional implicit patterns found in analysis:
- "Developer role complete" (builder.md entry conditions)
- "Implementation complete" (documenter.md)
- "Refactor role complete" (builder.md)
- "DoR complete" (developer.md)
- Shortened role names: "PO", "Project Owner" without "Assistant"
- **Recommendation:** Expand AC2 regex to include: `previous role|from the last|earlier phase|already created|role complete|implementation complete|DoR complete`

#### Issue 5: TechBestPractices.md path — NOT wrong (CLARIFICATION)
The `.github/roles/TechBestPractices.md` path is **correct for the deployed context** — after bootstrap, role files live in `.github/roles/`. When the LLM reads the role file during a workflow, TechBestPractices.md is at `.github/roles/TechBestPractices.md`. The path is only "wrong" relative to the package source directory.
- **Recommendation:** Keep `.github/roles/TechBestPractices.md` in the prose. For the front-matter `inputs:`, don't list it (it's a reference doc, not a work-item artifact).

## QA Summary
- 2 MEDIUM issues (refactor filename in design table, AC2 patterns incomplete)
- 3 LOW/CLARIFICATION issues
- Design is solid overall, proceed with corrections noted above

## Architect Notes

### Capability Impact
6 capabilities affected (1 direct: role-loader, 5 transitive). All impacts are NONE — no contract changes. See `GCP-0048-Capability-Impact.md` for details.

### Architectural Approval
- **YAML front-matter format**: Approved. Standard approach, no coupling to any Python parser.
- **No code changes**: Confirmed — only markdown files and one new test file.
- **Backward compatibility**: Validated — `output_validator.py` regex (`##\s*Required\s*Outputs`) is section-based, not position-based.
- **Security**: No concerns — no secrets, no new endpoints, no auth changes.

### Recommendations
1. Agree with QA Issue 2: use `{id}-refactor.md` (not `{id}-refactor-expert.md`) in front-matter to match `ROLE_SUFFIX_MAP`
2. Agree with QA Issue 5: Keep `.github/roles/TechBestPractices.md` in prose — it's the correct deployed path
3. Consider adding `domain-expert.md` optional output as a YAML comment in front-matter for clarity
