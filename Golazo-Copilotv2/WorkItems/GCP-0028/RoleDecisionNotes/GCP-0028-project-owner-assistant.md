# GCP-0028 Project Owner Assistant Notes

## Decision: Create TechBestPractices.md

### Context
Teams accumulate technical knowledge through experience (e.g., "don't use DefaultCredentials"). This knowledge is currently lost between sessions. A shared reference file prevents repeated mistakes.

### Alternatives Considered
1. **Embed in role files directly** - Makes role files bloated, hard to maintain
2. **Separate TechBestPractices.md file** - Clean separation, easy to update ✅ CHOSEN
3. **External documentation link** - Requires network access, not self-contained

### Implementation Approach
- Store in `defaults/TechBestPractices.md` in package
- Reference from Architect, Developer, Refactor role files
- Bootstrap copies it with other role files

### Initial Content
First best practice from user:
> "Never use DefaultCredentials from Azure Identity library; instead chain CLI and MSI creds"
