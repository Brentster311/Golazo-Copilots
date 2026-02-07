# GCP-0021: Design Document

## Summary
Update the refactor-expert role file to include a structured checklist of 10 OOP design principles with required rationale documentation for each.

## Problem Statement
The current refactor-expert role provides general guidance but lacks specific, actionable criteria. This leads to inconsistent refactoring depth. Adding a structured checklist with required rationale ensures consistent evaluation across all work items.

## Business Case
- **Why now**: GCP-0020 established "blocking > warning" principle; refactor role should follow same rigor
- **Impact**: Higher quality refactoring, consistent code review, educational value
- **KPIs**: All refactor notes include principle-by-principle evaluation

## Stakeholders
- AI Assistants (primary user of role file)
- Project Owners (benefit from documented refactor decisions)

## Functional Requirements
1. Add "Design Principles Checklist" section to refactor-expert.md
2. Include all 10 OOP principles with "Look For" guidance
3. Specify required rationale format (3 valid categories)
4. Document acceptable and unacceptable rationales

## Non-Functional Requirements
- Checklist should be concise (scannable)
- Language-agnostic principles

## Proposed Approach
1. Read current `golazo-instructions/roles/refactor-expert.md`
2. Add new section after "Responsibilities"
3. Include principles table and rationale framework
4. Preserve all existing content

## Alternatives Considered
| Alternative | Decision |
|-------------|----------|
| Blocking enforcement (new tool) | Rejected - adds complexity, rationale docs sufficient |
| Separate principles file | Rejected - keeps role self-contained |

## Risks & Mitigations
| Risk | Mitigation |
|------|------------|
| Role file becomes too long | Keep principles table concise |
| AI skips reading long sections | Bold key requirements |

## Dependencies
- None (standalone documentation change)

## Rollout Plan
1. Update role file
2. No migration needed - applies to future work items immediately

## Rollback Plan
- Revert role file to previous version

## Test Strategy
- Manual verification: role file contains all 10 principles
- Manual verification: rationale framework documented
