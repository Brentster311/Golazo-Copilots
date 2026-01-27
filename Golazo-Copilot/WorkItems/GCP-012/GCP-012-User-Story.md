# GCP-012: Pattern Research Guide for Infrastructure Changes

**Status**: IMPLEMENTED

## User Story

- **Title**: Create PatternProposals guide for infrastructure/config pattern research
- **As a**: Developer making infrastructure, pipeline, or config changes
- **I want**: A guide that ensures Copilot researches existing patterns before proposing new ones
- **So that**: New changes align with existing codebase conventions and avoid inventing inconsistent patterns

## Out of Scope

- Modifying role files
- Automated pattern detection tooling
- Changes to DoR/DoD gates

## Assumptions

- **Assumption (explicit)**: Guide will be loaded when Copilot detects infrastructure/config work
- **Assumption (explicit)**: Pattern research is advisory, not a blocking gate
- **Assumption (explicit)**: User must explicitly approve if new pattern differs from existing

## Acceptance Criteria (bulleted, testable)

- [ ] New file `.github/guides/PatternProposals.md` exists
- [ ] Guide has version header matching current Golazo version
- [ ] Guide includes "When to Use" section
- [ ] Guide includes 4-step research process: SEARCH, COUNT, PRESENT, APPROVE
- [ ] Guide includes "Fail-Fast Rule" for non-standard patterns
- [ ] Spine updated to reference guide in "Context-Specific Guides" section
- [ ] VERSION updated to 1.1.5
- [ ] CHANGELOG updated with GCP-012 entry

## Rollout / Rollback Notes

- **Rollout**: Create guide file, update spine reference, single commit
- **Rollback**: Revert commit (guide is additive)
