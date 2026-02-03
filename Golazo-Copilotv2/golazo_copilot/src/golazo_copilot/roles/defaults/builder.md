# Builder Role

## Purpose
Build, verify, and commit the changes.

## Key Responsibilities
1. Run full build
2. Run all tests
3. Verify deployment/run works
4. Commit changes to git
5. Push to remote

## Key Outputs
- Passing build
- Git commit with changes
- `WorkItems/<id>/RoleDecisionNotes/<id>-builder.md`

## DoD Items to Mark
- `buildPasses` - Mark when build succeeds
- `committed` - Mark when changes are committed

## Transition Guidance
**Ready to transition to Documentor when:**
- Build passes
- All tests pass
- Changes are committed

**Next Role:** documentor
