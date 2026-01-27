# GCP-009: Program Manager Decision Document

## Work Item
GCP-009 — Clarify Project Root Definition for Cross-IDE Compatibility

## Decisions Made

1. **Three-phase approach**
   - Phase 1: Add Project Root Definition section
   - Phase 2: Update artifact paths (remove `<ProjectName>`)
   - Phase 3: Add self-correction guidance

2. **VS Code manifest priority order**
   - Listed most common first: package.json, pyproject.toml
   - Includes broad coverage: Rust, Go, Java, C#, C/C++

3. **Fallback requires explicit confirmation**
   - Prevents silent wrong-location creation
   - User is aware and can correct immediately

4. **Include Repo Root vs Project Root distinction**
   - Addresses multi-project repository scenarios
   - Prevents confusion about where `.github/` lives vs where `WorkItems/` go

## Alternatives Considered

| Alternative | Rejected Because |
|-------------|------------------|
| Implicit fallback (no confirmation) | Could silently create files in wrong place |
| Complex heuristics | Over-engineering; simple rules suffice |
| IDE-specific instruction files | Adds maintenance burden |

## Tradeoffs Accepted

- Slightly longer spine document (adds ~50 lines)
- VS Code users without manifests have extra confirmation step

## Known Limitations or Risks

- Very unusual project structures may still confuse Copilot
- List of manifests may need updates as new languages/frameworks emerge

## Operational Impact

- No runtime impact (documentation only)
- No on-call considerations
- Rollback is simple git revert

## Next Role
Proceed to **Reviewer** for design review.
