# GCP-008 - Program Manager Decision Notes

## Work Item
GCP-008: Extract Technical Guides from Spine for Improved Copilot Interop

## Decisions Made

1. **Two-phase extraction**: Create guides first, then update spine (safer than simultaneous edit)
2. **Self-contained guides**: Each guide includes "When to use" section so it's useful standalone
3. **Version 1.1.0**: Minor version bump (backward-compatible structural change)
4. **Single commit deployment**: All changes together to avoid inconsistent state
5. **Update GCP-007 logic inline**: The upgrade process changes are part of this work item, not a separate story

## Alternatives Considered

| Alternative | Decision | Rationale |
|-------------|----------|-----------|
| Gradual rollout (spine first, guides later) | Rejected | Would leave spine with broken references |
| Major version (2.0.0) | Rejected | No breaking changes to workflow behavior |
| Separate story for upgrade process changes | Rejected | Integral to this refactor; can't ship without it |

## Tradeoffs Accepted

- **More files in upgrade process**: 13 files ? 15 files, but marginal complexity
- **Spine still references external files**: Could fail if guide is missing, but same pattern as roles

## Known Limitations

- Cannot objectively measure Copilot context efficiency
- "When to use" sections are guidance, not enforcement

## Risks

| Risk | Mitigation |
|------|------------|
| Breaking upgrade for users on 1.0.x | Test upgrade path from 1.0.11 ? 1.1.0 |
| Guide files not created in user repos | Upgrade process creates `.github/guides/` directory |

## Sequencing

1. Create directories
2. Create guide files (can exist without spine references)
3. Update spine (references now valid)
4. Update VERSION and CHANGELOG
5. Test workflow end-to-end
