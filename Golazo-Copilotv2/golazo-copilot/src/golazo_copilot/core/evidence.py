"""Evidence validation for DoR/DoD items - GCP-0023."""

from dataclasses import dataclass
from pathlib import Path
import subprocess
from typing import Union


@dataclass
class EvidenceResult:
    """Result of evidence validation."""
    valid: bool
    message: str
    normalized_path: str | None = None


# Evidence type mapping for each DoR/DoD item
FILE_EVIDENCE_ITEMS = {
    "userStory", "designDoc", "reviewComments", "testCases",
    "testsWrittenFirst", "docsUpdated", "refactorComplete", "retroComplete"
}

GIT_BRANCH_ITEMS = {"branchCreated"}
GIT_COMMIT_ITEMS = {"committed"}
COMMAND_EVIDENCE_ITEMS = {"testsPass", "buildPasses"}


def validate_file_evidence(
    evidence: Union[str, list[str]],
    workspace_path: Path
) -> EvidenceResult:
    """
    Validate that file(s) exist.
    
    Args:
        evidence: File path or list of file paths
        workspace_path: Workspace root for resolving relative paths
        
    Returns:
        EvidenceResult with validation status
    """
    if isinstance(evidence, str):
        paths = [evidence]
    else:
        paths = evidence
    
    if not paths:
        return EvidenceResult(
            valid=False,
            message="Empty evidence provided. Expected: file path(s)"
        )
    
    for path_str in paths:
        if not path_str or not path_str.strip():
            return EvidenceResult(
                valid=False,
                message="Empty path in evidence list"
            )
        
        # Resolve path (handle both relative and absolute)
        path = Path(path_str)
        if not path.is_absolute():
            path = workspace_path / path_str
        
        path = path.resolve()
        
        if not path.exists():
            return EvidenceResult(
                valid=False,
                message=f"File not found: '{path_str}'. Expected: valid file path. "
                        f"Example: 'WorkItems/GCP-0001/GCP-0001-User-Story.md'",
                normalized_path=str(path)
            )
        
        if not path.is_file():
            return EvidenceResult(
                valid=False,
                message=f"Path exists but is not a file: '{path_str}'. "
                        "Evidence must point to a file, not a directory.",
                normalized_path=str(path)
            )
    
    # All files valid
    normalized = str((workspace_path / paths[0]).resolve()) if len(paths) == 1 else None
    return EvidenceResult(valid=True, message="", normalized_path=normalized)


def validate_git_branch(branch_name: str, workspace_path: Path) -> EvidenceResult:
    """
    Validate that a git branch exists.
    
    Args:
        branch_name: Name of the branch to check
        workspace_path: Path to run git command from
        
    Returns:
        EvidenceResult with validation status
    """
    if not branch_name or not branch_name.strip():
        return EvidenceResult(
            valid=False,
            message="Empty branch name provided"
        )
    
    try:
        result = subprocess.run(
            ["git", "branch", "--list", branch_name],
            cwd=workspace_path,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=5
        )
        
        # Check if branch is in output
        if branch_name in result.stdout:
            return EvidenceResult(valid=True, message="", normalized_path=branch_name)
        else:
            return EvidenceResult(
                valid=False,
                message=f"Git branch not found: '{branch_name}'. "
                        "Expected: existing branch name. "
                        "Create with: git checkout -b <branch-name>",
                normalized_path=None
            )
    except FileNotFoundError:
        return EvidenceResult(
            valid=False,
            message="Git is not available. Please ensure git is installed and in PATH.",
            normalized_path=None
        )
    except subprocess.TimeoutExpired:
        return EvidenceResult(
            valid=False,
            message="Git command timed out",
            normalized_path=None
        )


def validate_git_commit(sha: str, workspace_path: Path) -> EvidenceResult:
    """
    Validate that a git commit exists.
    
    Args:
        sha: Commit SHA (full or short, 7+ chars)
        workspace_path: Path to run git command from
        
    Returns:
        EvidenceResult with validation status
    """
    if not sha or not sha.strip():
        return EvidenceResult(
            valid=False,
            message="Empty commit SHA provided"
        )
    
    if len(sha.strip()) < 7:
        return EvidenceResult(
            valid=False,
            message=f"Commit SHA too short: '{sha}'. Expected: at least 7 characters"
        )
    
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--verify", sha],
            cwd=workspace_path,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=5
        )
        
        if result.returncode == 0:
            return EvidenceResult(
                valid=True,
                message="",
                normalized_path=result.stdout.strip()
            )
        else:
            return EvidenceResult(
                valid=False,
                message=f"Git commit not found: '{sha}'. "
                        "Expected: valid commit SHA (7+ characters). "
                        "Get current: git rev-parse HEAD",
                normalized_path=None
            )
    except FileNotFoundError:
        return EvidenceResult(
            valid=False,
            message="Git is not available. Please ensure git is installed and in PATH.",
            normalized_path=None
        )
    except subprocess.TimeoutExpired:
        return EvidenceResult(
            valid=False,
            message="Git command timed out",
            normalized_path=None
        )


def validate_command_evidence(evidence: str) -> EvidenceResult:
    """
    Validate command-based evidence (test output, CI links).
    
    Args:
        evidence: Command output or CI link
        
    Returns:
        EvidenceResult with validation status
    """
    if not evidence or not evidence.strip():
        return EvidenceResult(
            valid=False,
            message="Empty evidence provided. Expected: command output or CI link. "
                    "Example: 'pytest: 113 passed in 1.2s' or 'https://ci.example.com/build/123'"
        )
    
    return EvidenceResult(valid=True, message="", normalized_path=None)


def validate_evidence(
    item: str,
    evidence: Union[str, list[str]],
    workspace_path: Path
) -> EvidenceResult:
    """
    Validate evidence for a specific DoR/DoD item.
    
    Args:
        item: DoR/DoD item name (e.g., 'userStory', 'testsPass')
        evidence: Evidence value
        workspace_path: Workspace root
        
    Returns:
        EvidenceResult with validation status
    """
    if item in FILE_EVIDENCE_ITEMS:
        return validate_file_evidence(evidence, workspace_path)
    
    if item in GIT_BRANCH_ITEMS:
        if not isinstance(evidence, str):
            return EvidenceResult(
                valid=False,
                message=f"Branch name must be a string, got {type(evidence).__name__}"
            )
        return validate_git_branch(evidence, workspace_path)
    
    if item in GIT_COMMIT_ITEMS:
        if not isinstance(evidence, str):
            return EvidenceResult(
                valid=False,
                message=f"Commit SHA must be a string, got {type(evidence).__name__}"
            )
        return validate_git_commit(evidence, workspace_path)
    
    if item in COMMAND_EVIDENCE_ITEMS:
        if not isinstance(evidence, str):
            return EvidenceResult(
                valid=False,
                message=f"Command evidence must be a string, got {type(evidence).__name__}"
            )
        return validate_command_evidence(evidence)
    
    # Unknown item - accept any non-empty evidence
    if isinstance(evidence, str) and not evidence.strip():
        return EvidenceResult(
            valid=False,
            message=f"Empty evidence provided for '{item}'"
        )
    
    return EvidenceResult(valid=True, message="")


def get_evidence_hint(item: str, work_item_id: str = "<id>") -> str:
    """
    Get a helpful hint about what evidence is expected for an item.
    
    Args:
        item: The DoR/DoD item name
        work_item_id: Work item ID for example paths
        
    Returns:
        Human-readable hint string
    """
    hints = {
        # DoR items
        "userStory": f"File path to User Story markdown (e.g., 'WorkItems/{work_item_id}/{work_item_id}-User-Story.md')",
        "designDoc": f"File path to Design Doc (e.g., 'WorkItems/{work_item_id}/Design/{work_item_id}-design-doc.md')",
        "reviewComments": f"File path to Review Comments (e.g., 'WorkItems/{work_item_id}/Design/{work_item_id}-Review-Comments.md')",
        "testCases": f"File path to Test Cases (e.g., 'WorkItems/{work_item_id}/Design/{work_item_id}-Test-Cases.md')",
        # DoD items
        "branchCreated": "Git branch name (e.g., 'feature/GCP-0001')",
        "testsWrittenFirst": "File path(s) to test files (e.g., 'tests/test_feature.py')",
        "testsPass": "Command output or CI link showing tests pass (e.g., 'pytest output: 29 passed')",
        "buildPasses": "Command output or CI link showing build passes (e.g., 'Build successful')",
        "docsUpdated": "File path(s) to updated docs (e.g., 'README.md')",
        "refactorComplete": f"File path to Refactoring Plan (e.g., 'WorkItems/{work_item_id}/Design/{work_item_id}-Refactoring-Plan.md')",
        "committed": "Git commit SHA (e.g., 'abc1234')",
        "retroComplete": f"File path to Retro Plan (e.g., 'WorkItems/{work_item_id}/Design/{work_item_id}-Retro-Plan.md')",
    }
    return hints.get(item, "Evidence string describing the completed work")
