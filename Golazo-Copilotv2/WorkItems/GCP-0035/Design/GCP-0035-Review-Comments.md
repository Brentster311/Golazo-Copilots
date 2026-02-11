# GCP-0035 — Review Comments

## Design Review

### Clarity & Completeness
- Design clearly identifies the 7 correctness issues and 5 completeness gaps. Approach (selective rewrite) is sound.

### Risks
- **Stale references**: Design includes grep-based verification — good.
- **Azure Artifacts URL**: Must verify the feed URL in the README matches the actual `.pypirc` feed URL. Currently both use `azinsights_accia_pkgs` — confirmed consistent.

### Recommendations
1. After rewrite, verify no orphaned internal markdown links (e.g., anchor links to removed sections)
2. Ensure the "Workflow Profiles" table still makes sense without DoR/DoD item-level detail — describe profiles in terms of which roles are included/skipped

### Verdict
Approved. Proceed with implementation.
