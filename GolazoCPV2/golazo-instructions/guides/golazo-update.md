<!-- Golazo Version: 1.1.0 -->
# Golazo Update Guide

## When to Use

Consult this guide when:
- Starting a new Golazo session (check if 24+ hours since last update check)
- User says "check for Golazo updates"
- User wants to upgrade Golazo to a newer version

---

## When to Check for Updates

- Check for updates when starting a new Golazo session **if** more than 24 hours have passed since the last check
- The timestamp of the last check is stored in `.github/.golazo-update-check`
- User can also request a check at any time by saying "check for Golazo updates"

---

## How to Check for Updates

### Step 1: Read local version

Read line 1 of `.github/copilot-instructions.md` (format: `<!-- Golazo Version: X.Y.Z -->`)

### Step 2: Fetch remote version

```powershell
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/Brentster311/Golazo-Copilots/main/Golazo-Copilot/VERSION" -UseBasicParsing -TimeoutSec 5 | Select-Object -ExpandProperty Content
```

### Step 3: Compare versions (semantic versioning)

- Parse both as MAJOR.MINOR.PATCH
- If remote > local, update is available
- If remote <= local, already up to date

### Step 4: Update the timestamp file

```powershell
Get-Date -Format "o" | Set-Content ".github/.golazo-update-check" -NoNewline
```

---

## If Update Available

Display to user:
```
?? **Golazo Update Available**
- Installed: v{local_version}
- Available: v{remote_version}

**What's new in v{remote_version}:**
{relevant changelog entries}

Would you like to upgrade? (yes/no)
```

Fetch changelog from: `https://raw.githubusercontent.com/Brentster311/Golazo-Copilots/main/Golazo-Copilot/CHANGELOG.md`

Show only entries between current and target version.

---

## Upgrade Process (if user confirms)

### Step 1: Create backup of existing files

```powershell
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backupDir = ".github/backup/$timestamp"
New-Item -ItemType Directory -Path $backupDir -Force
Copy-Item ".github/copilot-instructions.md" "$backupDir/"
Copy-Item ".github/roles/*.md" "$backupDir/" -Force
Copy-Item ".github/guides/*.md" "$backupDir/" -Force -ErrorAction SilentlyContinue
```

### Step 2: Ensure guides directory exists

```powershell
New-Item -ItemType Directory -Path ".github/guides" -Force
```

### Step 3: Download all files from GitHub (all-or-nothing approach)

```powershell
$baseUrl = "https://raw.githubusercontent.com/Brentster311/Golazo-Copilots/main/Golazo-Copilot"

# Download spine
Invoke-WebRequest -Uri "$baseUrl/.github/copilot-instructions.md" -OutFile ".github/copilot-instructions.md"

# Download each role file
$roles = @("project-owner-assistant", "program-manager", "reviewer", "architect", "tester", "developer", "refactor-expert", "builder", "documentor", "retrospective")
foreach ($role in $roles) {
    Invoke-WebRequest -Uri "$baseUrl/.github/roles/$role.md" -OutFile ".github/roles/$role.md"
}

# Download guide files
$guides = @("powershell-terminal", "golazo-update")
foreach ($guide in $guides) {
    Invoke-WebRequest -Uri "$baseUrl/.github/guides/$guide.md" -OutFile ".github/guides/$guide.md"
}
```

### Step 4: Verify downloads - if any download fails, restore from backup

```powershell
# If download failed, restore backup
Copy-Item "$backupDir/*" ".github/" -Force
Copy-Item "$backupDir/*.md" ".github/roles/" -Force -ErrorAction SilentlyContinue
Copy-Item "$backupDir/*.md" ".github/guides/" -Force -ErrorAction SilentlyContinue
```

### Step 5: Report result

- Success: `? Golazo upgraded to v{new_version}. Backup saved to {backup_path}`
- Failure: `? Upgrade failed: {reason}. Original files preserved.`

---

## If Already Up to Date

Display: `? Golazo is up to date (v{local_version})`

---

## If Network Error

Display: `?? Could not check for updates (network error). Continuing normally.`

Do NOT block the user's workflow. Continue with normal Golazo operation.

---

## Files Downloaded During Upgrade

### Spine (1 file)
1. `.github/copilot-instructions.md`

### Role Files (10 files)
2. `.github/roles/project-owner-assistant.md`
3. `.github/roles/program-manager.md`
4. `.github/roles/reviewer.md`
5. `.github/roles/architect.md`
6. `.github/roles/tester.md`
7. `.github/roles/developer.md`
8. `.github/roles/refactor-expert.md`
9. `.github/roles/builder.md`
10. `.github/roles/documentor.md`
11. `.github/roles/retrospective.md`

### Guide Files (2 files)
12. `.github/guides/powershell-terminal.md`
13. `.github/guides/golazo-update.md`

**Total: 13 files**
