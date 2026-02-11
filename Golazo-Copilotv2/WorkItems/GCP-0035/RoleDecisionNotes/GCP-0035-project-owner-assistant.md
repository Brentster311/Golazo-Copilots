# GCP-0035 — Project Owner Assistant Decision Notes

## Decision: Single story vs. decomposition
The README rewrite is a single deliverable (one file) with no code changes, so it stays as one story. No decomposition needed.

## Scope rationale
Limited strictly to README.md content. The review identified 7 correctness issues (all stemming from the DoR/DoD → output validation pivot) and 5 completeness gaps. All are documentation-only fixes.

## Key decisions
- **Remove, don't update** the Evidence-Based Validation section — it documents a deleted system, patching it would be confusing
- **Replace DoR/DoD sections** with a new "Role-Based Output Validation" section that explains the `## Required Outputs` mechanism
- **Preserve** the Installation, Configuration, and Troubleshooting sections — these are still accurate
- **Add** sections for GCP-0032 (version sync), GCP-0033 (role progress), GCP-0028 (TechBestPractices), GCP-0026 (Required Outputs format)

## Must-Ask resolution
All established from prior work: MCP server, cross-platform, file-based persistence, developer audience.
