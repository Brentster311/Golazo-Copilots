"""Output validator for role-based validation - GCP-0025.

Parses Required Outputs section from role files and validates each output exists.
"""

import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class OutputSpec:
    """Specification for a required output."""
    type: str  # "file", "dir", "git-branch", "git-log"
    path_or_pattern: str
    closure_only: bool = False


@dataclass
class ValidationResult:
    """Result of validating all outputs."""
    valid: bool
    message: str
    outputs: list = field(default_factory=list)  # List of {spec, valid, message}


def parse_required_outputs(role_content: str, work_item_id: str) -> list[OutputSpec]:
    """
    Parse the Required Outputs section from a role file.
    
    Args:
        role_content: Full content of the role markdown file
        work_item_id: Work item ID to substitute for {id} placeholder
        
    Returns:
        List of OutputSpec objects
    """
    outputs = []
    
    # Find the Required Outputs section
    # Match "## Required Outputs" followed by content until next ## or end
    section_pattern = r'##\s*Required\s*Outputs\s*\n(.*?)(?=\n##|\Z)'
    match = re.search(section_pattern, role_content, re.DOTALL | re.IGNORECASE)
    
    if not match:
        return outputs
    
    section_content = match.group(1)
    
    # Parse each line that starts with "- type: value"
    # Belt-and-suspenders: also strip inline HTML comments from paths
    line_pattern = r'^\s*-\s*(file|dir|git-branch|git-log):\s*(.+?)\s*(?:<!--.*?-->)?\s*$'
    
    next_is_closure_only = False
    
    for line in section_content.split('\n'):
        stripped = line.strip()
        
        # Detect <!-- closure-only --> annotation on its own line
        if stripped == '<!-- closure-only -->':
            next_is_closure_only = True
            continue
        
        # Skip other HTML comments
        if stripped.startswith('<!--'):
            continue
            
        line_match = re.match(line_pattern, line, re.IGNORECASE)
        if line_match:
            output_type = line_match.group(1).lower()
            path_or_pattern = line_match.group(2)
            
            # Substitute {id} placeholder
            path_or_pattern = path_or_pattern.replace('{id}', work_item_id)
            
            outputs.append(OutputSpec(
                type=output_type,
                path_or_pattern=path_or_pattern,
                closure_only=next_is_closure_only,
            ))
            next_is_closure_only = False
        elif stripped:  # Non-empty non-matching line resets the annotation
            next_is_closure_only = False
        else:  # Blank line also resets annotation (must be immediately adjacent)
            next_is_closure_only = False
    
    return outputs


def validate_output(spec: OutputSpec, workspace_path: Path) -> dict:
    """
    Validate a single output exists.
    
    Args:
        spec: The output specification
        workspace_path: Workspace root for resolving paths
        
    Returns:
        Dict with valid, message, and spec info
    """
    if spec.type == "file":
        return _validate_file(spec, workspace_path)
    elif spec.type == "dir":
        return _validate_dir(spec, workspace_path)
    elif spec.type == "git-branch":
        return _validate_git_branch(spec, workspace_path)
    elif spec.type == "git-log":
        return _validate_git_log(spec, workspace_path)
    else:
        return {
            "valid": False,
            "message": f"Unknown output type: {spec.type}",
            "spec": spec,
        }


def _validate_file(spec: OutputSpec, workspace_path: Path) -> dict:
    """Validate file exists."""
    path = workspace_path / spec.path_or_pattern
    
    if not path.exists():
        return {
            "valid": False,
            "message": f"File not found: {spec.path_or_pattern}",
            "spec": spec,
        }
    
    if not path.is_file():
        return {
            "valid": False,
            "message": f"Path exists but is not a file: {spec.path_or_pattern}",
            "spec": spec,
        }
    
    return {"valid": True, "message": "", "spec": spec}


def _validate_dir(spec: OutputSpec, workspace_path: Path) -> dict:
    """Validate directory exists."""
    path = workspace_path / spec.path_or_pattern
    
    if not path.exists():
        return {
            "valid": False,
            "message": f"Directory not found: {spec.path_or_pattern}",
            "spec": spec,
        }
    
    if not path.is_dir():
        return {
            "valid": False,
            "message": f"Path exists but is not a directory: {spec.path_or_pattern}",
            "spec": spec,
        }
    
    return {"valid": True, "message": "", "spec": spec}


def _validate_git_branch(spec: OutputSpec, workspace_path: Path) -> dict:
    """Validate git branch exists matching pattern."""
    try:
        result = subprocess.run(
            ["git", "branch", "--list", spec.path_or_pattern],
            cwd=workspace_path,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=5
        )
        
        if result.stdout.strip():
            return {"valid": True, "message": "", "spec": spec}
        else:
            return {
                "valid": False,
                "message": f"Git branch not found: {spec.path_or_pattern}",
                "spec": spec,
            }
    except FileNotFoundError:
        return {
            "valid": False,
            "message": "Git not available - skipping branch validation",
            "spec": spec,
        }
    except subprocess.TimeoutExpired:
        return {
            "valid": False,
            "message": "Git command timed out",
            "spec": spec,
        }


def _validate_git_log(spec: OutputSpec, workspace_path: Path) -> dict:
    """Validate git log contains commit matching pattern."""
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "--all", f"--grep={spec.path_or_pattern}"],
            cwd=workspace_path,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=5
        )
        
        if result.stdout.strip():
            return {"valid": True, "message": "", "spec": spec}
        else:
            return {
                "valid": False,
                "message": f"No commit found matching: {spec.path_or_pattern}",
                "spec": spec,
            }
    except FileNotFoundError:
        return {
            "valid": False,
            "message": "Git not available - skipping log validation",
            "spec": spec,
        }
    except subprocess.TimeoutExpired:
        return {
            "valid": False,
            "message": "Git command timed out",
            "spec": spec,
        }


def validate_all_outputs(specs: list[OutputSpec], workspace_path: Path) -> ValidationResult:
    """
    Validate all output specifications.
    
    Args:
        specs: List of output specifications
        workspace_path: Workspace root
        
    Returns:
        ValidationResult with overall status and per-output details
    """
    if not specs:
        return ValidationResult(valid=True, message="", outputs=[])
    
    results = []
    missing = []
    
    for spec in specs:
        result = validate_output(spec, workspace_path)
        results.append(result)
        if not result["valid"]:
            missing.append(spec.path_or_pattern)
    
    if missing:
        message = f"Missing required outputs: {', '.join(missing)}"
        return ValidationResult(valid=False, message=message, outputs=results)
    
    return ValidationResult(valid=True, message="", outputs=results)
