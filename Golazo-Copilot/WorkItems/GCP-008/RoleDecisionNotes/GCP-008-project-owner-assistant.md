# GCP-008 - Project Owner Assistant Decision Notes

## Work Item
GCP-008: Extract Technical Guides from Spine for Improved Copilot Interop

## Decisions Made

1. **Scope limited to two extractions**: PowerShell terminal rules and Golazo update logic
2. **No new roles created**: These are technical reference guides, not workflow roles
3. **No shared-definitions file**: Role files are small enough; centralization adds complexity without benefit
4. **No keyword detection**: Explicit spine references are sufficient; Copilot handles relevance naturally
5. **Version bump to 1.1.0**: Minor version for backward-compatible structural change

## Alternatives Considered

| Alternative | Decision | Rationale |
|-------------|----------|-----------|
| Keep everything in spine | Rejected | ~37% of spine is situationally relevant; wastes context tokens |
| Create new workflow roles for PowerShell/Update | Rejected | These aren't workflow steps; they're technical references |
| Extract shared definitions (paths, common rules) | Rejected | Role files are already small; adds indirection without benefit |
| Major version bump (2.0.0) | Rejected | No breaking changes; workflow behavior unchanged |

## Tradeoffs Accepted

- **More files to maintain**: 2 additional guide files, but they're stable content unlikely to change frequently
- **Explicit loading required**: Users/Copilot must reference guides explicitly, but this is the desired behavior (load only when relevant)

## Known Limitations

- Cannot measure Copilot context efficiency directly; improvement is theoretical based on reduced always-loaded content
- Guides must be manually kept in sync with any future spine changes that affect their content

## Risks

| Risk | Mitigation |
|------|------------|
| Copilot might not load guides when needed | Clear "Context-Specific Guides" section in spine with explicit triggers |
| Guides become stale | Include version headers; update process includes all guide files |
| Upgrade process breaks | Update GCP-007 upgrade logic to include guide files in download list |

## Questions Answered by Project Owner

1. File structure proposal ? **Approved**
2. Explicit loading in spine ? **Yes, try this approach**
3. Keyword detection ? **Not needed**
4. Shared definitions ? **No, not worth it**
5. Version headers in guides ? **Yes**
6. Version bump ? **Yes, this is a major refactor**
