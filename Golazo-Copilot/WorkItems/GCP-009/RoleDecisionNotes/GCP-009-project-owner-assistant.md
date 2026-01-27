# GCP-009: Project Owner Assistant Decision Document

## Work Item
GCP-009 — Clarify Project Root Definition for Cross-IDE Compatibility

## Decisions Made

1. **Remove `<ProjectName>` token entirely**
   - Source of confusion for Copilot
   - Replace with explicit relative paths from Project Root

2. **Define Project Root per IDE**
   - Visual Studio: Directory containing active `.proj` file
   - VS Code: Directory containing project manifest, with fallback

3. **VS Code fallback requires confirmation**
   - If no manifest found, use workspace folder
   - BUT confirm with Project Owner before creating artifacts
   - Prevents incorrect file placement in ambiguous situations

4. **Document Repo Root vs Project Root distinction**
   - Repo Root: Contains `.git/` and `.github/`
   - Project Root: Contains project file (where artifacts go)
   - These may be the same OR different (multi-project repos)

## Must-Ask Checklist Results

| Question | Answer |
|----------|--------|
| Interface type | N/A (documentation change) |
| Target platform | Cross-platform (VS + VS Code) |
| Data persistence | Markdown files |
| User type | Developers |

## Alternatives Considered

| Alternative | Rejected Because |
|-------------|------------------|
| Always use Repo Root | Doesn't work for multi-project repos |
| Explicit `.golazo-project` marker file | Extra setup burden on users |
| VS Code always uses workspace root | May be wrong for monorepos |

## Tradeoffs Accepted

- VS Code users without standard project manifests need to confirm location
- Slightly more complex rules than "always use X"

## Known Limitations or Risks

- Copilot may still occasionally misinterpret if project structure is unusual
- Users with non-standard project layouts may need manual guidance

## Next Role
Proceed to **Program Manager** for Design Doc.
