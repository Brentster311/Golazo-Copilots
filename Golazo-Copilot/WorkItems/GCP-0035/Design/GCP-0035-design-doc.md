# GCP-0035 Design Document: Rewrite README for Output Validation Architecture

## Summary
Rewrite the golazo-copilot README.md to remove all references to the deleted DoR/DoD checklist system and replace them with documentation for the current role-based output validation architecture, plus document features added since the original README was written.

## Problem Statement
The README documents a system that no longer exists. ~40% of the feature documentation describes DoR/DoD marking tools (`gcp_mark_dor`, `gcp_mark_dod`), evidence validation, and checklist items that were removed by GCP-0025, GCP-0027, and GCP-0031. New users following the README will encounter tools that don't exist and workflows that fail.

## Business Case
- **Why now**: The README is the primary onboarding document. Every new user hits incorrect instructions immediately.
- **Impact**: Eliminates confusion for all new adopters.
- **KPIs**: Zero references to deleted tools/systems in README.

## Stakeholders
- New users installing Golazo Copilot
- Existing users upgrading versions

## Functional Requirements
1. Remove Evidence-Based Validation section entirely
2. Replace DoR Gates section with Role-Based Output Validation section
3. Replace DoD Tracking section (or merge into output validation)
4. Update tools table to list only 5 actual tools
5. Update "Verify MCP Server" section tool list
6. Fix example session to use current workflow
7. Update workflow profiles to reference output validation, not DoR/DoD items
8. Add documentation for: version sync warning, role progress display, TechBestPractices, Required Outputs format

## Non-Functional Requirements
- Maintain existing README structure (Features → Installation → Configuration → Usage → Troubleshooting)
- Keep installation/troubleshooting sections accurate (they're mostly fine)
- README should remain scannable with tables and code blocks

## Proposed Approach
Single-pass rewrite of README.md:
1. Keep: header, "What is Golazo?", Persistent State, Role Transitions, Multi-Session, Deviation Recording, Role Notes sections
2. Remove: Evidence-Based Validation, DoR Gates (item-level), DoD Tracking (item-level)
3. Replace with: Role-Based Output Validation section
4. Update: Workflow Profiles, Tools table, Example Session, Verify section
5. Add: Version Sync Warning, Role Progress, TechBestPractices subsections

## Alternatives Considered
- **Patch individual sections** — Rejected: too many interrelated changes, cleaner to rewrite affected sections
- **Complete rewrite from scratch** — Rejected: ~60% of the README is still accurate (installation, config, troubleshooting)

## Risks & Mitigations
| Risk | Mitigation |
|------|------------|
| Lose accurate installation instructions | Preserve Prerequisites, Installation, and Troubleshooting sections verbatim unless corrections needed |
| Miss a stale reference | Grep for `mark_dor`, `mark_dod`, `evidence`, `DoR`, `DoD` after rewrite |

## Dependencies
- None — documentation only

## Migration / Rollout
- Publish updated README with next version bump
- No backward compatibility concerns

## Test Strategy
- Grep README for removed terms (`gcp_mark_dor`, `gcp_mark_dod`, `evidence`, `DoR gate`, `DoD tracking`)
- Verify all 5 actual tools are listed
- Verify new features (version sync, role progress, TechBestPractices) are documented
