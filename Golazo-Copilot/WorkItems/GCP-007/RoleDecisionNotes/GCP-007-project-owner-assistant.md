# GCP-007: Project Owner Assistant Notes

**Work Item**: GCP-007 - Golazo Copilot Update Detection and Upgrade  
**Date**: 2026-01-20

## Decisions Made

1. **Update source**: GitHub raw files
   - `https://raw.githubusercontent.com/Brentster311/Golazo-Copilots/main/VERSION`
   - `https://raw.githubusercontent.com/Brentster311/Golazo-Copilots/main/CHANGELOG.md`
   - Simple, no authentication required, works anywhere with internet

2. **Detection mechanism**: Instructions in spine file tell Copilot how to check
   - Copilot uses `get_web_pages` tool or `run_command_in_terminal` with curl/Invoke-WebRequest
   - Compares remote VERSION to local version comment in spine

3. **User experience flow**:
   - Copilot detects newer version available
   - Shows: "Golazo v1.0.0 installed. v1.1.0 available."
   - Shows relevant CHANGELOG entries
   - Asks: "Would you like to upgrade? (yes/no)"
   - User must explicitly confirm before any files are modified

4. **Upgrade mechanism**: Terminal commands
   - PowerShell: `Invoke-WebRequest -Uri <url> -OutFile <path>`
   - Downloads spine file + all role files from GitHub raw URLs
   - Overwrites local `.github/` files

5. **Trigger timing**: On-demand or periodic suggestion
   - Copilot may suggest checking on session start
   - User can also ask "check for Golazo updates" at any time

## Alternatives Considered

| Alternative | Why Rejected |
|-------------|--------------|
| Azure Artifacts | Requires auth, complex setup, overkill for MD files |
| GitHub Releases API | More complex, requires JSON parsing |
| Golazo_Copilot.py update command | User may not have Python script installed |
| Auto-update without asking | Violates user consent principle |

## Tradeoffs Accepted
- Depends on GitHub availability (acceptable for open-source project)
- Requires internet access (offline users must update manually)
- Version comparison is string-based (assumes semantic versioning compliance)

## Known Limitations
- Cannot detect if user has local modifications to instruction files
- No rollback mechanism (user can manually restore from git)
- Network errors may cause false "up to date" if fetch fails silently

## Dependencies
- **Requires GCP-006** (version metadata in files)

## Resolved Questions (from Project Owner)
1. **Should we add a "last checked" timestamp?** ? Yes
2. **Should upgrade backup existing files before overwriting?** ? Yes (to `.github/backup/`)
3. **What branch should be the update source?** ? `main`

## Open Questions for Architect
1. What's the complete list of files to download during upgrade?
2. Where should the "last checked" timestamp be stored?
3. How long should the check interval be (e.g., once per day, once per session)?
