"""Bootstrap tool for Golazo Copilot."""

from pathlib import Path
from importlib import resources
import shutil


# Workspace markers - at least one must exist
WORKSPACE_MARKERS = [".git", "pyproject.toml", "package.json", "Cargo.toml", ".hg"]

# Default role files to copy
DEFAULT_ROLES = [
    "project-owner-assistant.md",
    "program-manager.md",
    "quality-assurance.md",
    "architect.md",
    "developer.md",
    "refactor-expert.md",
    "builder.md",
    "documentor.md",
    "retrospective.md",
]


def _is_workspace(path: Path) -> bool:
    """Check if path is a valid workspace root."""
    return any((path / marker).exists() for marker in WORKSPACE_MARKERS)


def _get_default_instructions() -> str:
    """Get default copilot instructions content."""
    return '''# Golazo Copilot v2

This workspace uses Golazo Copilot MCP server for workflow management.

## REQUIRED: Before EVERY Response
1. Call `gcp_status(work_item_id="<current-id>")` to get current state
2. Display the Golazo Status header
3. Follow the role instructions returned
4. If no active work item, ask user which to start

---

## Starting a New Work Item
```
gcp_create_workitem(work_item_id="<id>", profile="complete")
```
Then create User Story at `WorkItems/<id>/<id>-User-Story.md`

---

## Marking Progress (IMPORTANT: use `complete` not `value`)

After creating **User Story**:
```
gcp_mark_dor(work_item_id="<id>", item="userStory", complete=true)
```

After creating **Design Doc**:
```
gcp_mark_dor(work_item_id="<id>", item="designDoc", complete=true)
```

After creating **Review Comments**:
```
gcp_mark_dor(work_item_id="<id>", item="reviewComments", complete=true)
```

After creating **Test Cases**:
```
gcp_mark_dor(work_item_id="<id>", item="testCases", complete=true)
```

---

## Role Transitions

To move to next role:
```
gcp_transition(work_item_id="<id>", role="program-manager")
```

**Valid roles in order:**
1. project-owner-assistant
2. program-manager
3. quality-assurance
4. architect
5. developer (requires DoR complete!)
6. refactor-expert
7. builder
8. documentor
9. retrospective

---

## DoD Items (after development)

```
gcp_mark_dod(work_item_id="<id>", item="branchCreated", complete=true)
gcp_mark_dod(work_item_id="<id>", item="testsWrittenFirst", complete=true)
gcp_mark_dod(work_item_id="<id>", item="testsPass", complete=true)
gcp_mark_dod(work_item_id="<id>", item="buildPasses", complete=true)
gcp_mark_dod(work_item_id="<id>", item="docsUpdated", complete=true)
gcp_mark_dod(work_item_id="<id>", item="refactorComplete", complete=true)
gcp_mark_dod(work_item_id="<id>", item="committed", complete=true)
```

---

## File Naming Convention (ENFORCE)

| Artifact | Path |
|----------|------|
| User Story | `WorkItems/<id>/<id>-User-Story.md` |
| Design Doc | `WorkItems/<id>/Design/<id>-design-doc.md` |
| Review Comments | `WorkItems/<id>/Design/<id>-Review-Comments.md` |
| Test Cases | `WorkItems/<id>/Design/<id>-Test-Cases.md` |
| Role Notes | `WorkItems/<id>/RoleDecisionNotes/<id>-<role>.md` |

---

## Each Role MUST Create:
- **Project Owner Assistant**: User Story + `<id>-project-owner-assistant.md`
- **Program Manager**: Design Doc + `<id>-program-manager.md`
- **Quality Assurance**: Review Comments + Test Cases + `<id>-quality-assurance.md`
- **Architect**: Architect notes in Review Comments + `<id>-architect.md`
- **Developer**: Code + Tests + `<id>-developer.md`
- **Refactor Expert**: Refactored code + `<id>-refactor-expert.md`
- **Builder**: Build/commit + `<id>-builder.md`
- **Documentor**: Updated docs + `<id>-documentor.md`

---

## Gate Enforcement
- **DoR Gate**: Cannot transition to `developer` until ALL DoR items are complete
- If `gcp_transition` fails, call `gcp_status` to see what's missing
'''


async def gcp_bootstrap(
    workspace_path: Path | str | None = None,
    force: bool = False,
    include_roles: bool = False,
) -> dict:
    """
    Bootstrap Golazo Copilot in a workspace.
    
    Creates:
    - .github/copilot-instructions.md
    - WorkItems/.gitkeep
    - Optionally: .github/roles/*.md
    
    Args:
        workspace_path: Workspace root path (auto-detected if not provided)
        force: Overwrite existing files if they exist
        include_roles: Also copy default role files to .github/roles/
    
    Returns:
        Dict with success status and list of created/skipped files.
    """
    # Resolve workspace path
    if workspace_path is None:
        workspace_path = Path.cwd()
    else:
        workspace_path = Path(workspace_path)
    
    # Validate workspace
    if not _is_workspace(workspace_path):
        return {
            "success": False,
            "error": f"Not a valid workspace. No workspace markers found ({', '.join(WORKSPACE_MARKERS)})",
            "files_created": [],
            "files_skipped": [],
        }
    
    files_created = []
    files_skipped = []
    
    # Create .github directory
    github_dir = workspace_path / ".github"
    github_dir.mkdir(parents=True, exist_ok=True)
    
    # Create copilot-instructions.md
    instructions_path = github_dir / "copilot-instructions.md"
    if instructions_path.exists() and not force:
        files_skipped.append(".github/copilot-instructions.md")
    else:
        instructions_path.write_text(_get_default_instructions(), encoding="utf-8")
        files_created.append(".github/copilot-instructions.md")
    
    # Create WorkItems directory
    workitems_dir = workspace_path / "WorkItems"
    workitems_dir.mkdir(parents=True, exist_ok=True)
    
    # Create .gitkeep
    gitkeep_path = workitems_dir / ".gitkeep"
    if not gitkeep_path.exists():
        gitkeep_path.write_text("", encoding="utf-8")
        files_created.append("WorkItems/.gitkeep")
    
    # Optionally copy role files
    if include_roles:
        roles_dir = github_dir / "roles"
        roles_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Load role files from package
            role_files = resources.files("golazo_copilot.roles.defaults")
            for role_name in DEFAULT_ROLES:
                role_file = role_files.joinpath(role_name)
                dest_path = roles_dir / role_name
                
                if dest_path.exists() and not force:
                    files_skipped.append(f".github/roles/{role_name}")
                else:
                    content = role_file.read_text(encoding="utf-8")
                    dest_path.write_text(content, encoding="utf-8")
                    files_created.append(f".github/roles/{role_name}")
        except Exception as e:
            # If package resources fail, still succeed but note it
            pass
    
    return {
        "success": True,
        "files_created": files_created,
        "files_skipped": files_skipped,
        "message": f"Bootstrapped Golazo Copilot in {workspace_path}",
    }
