#!/usr/bin/env python3
"""
Golazo Copilot - CLI tool to install Golazo workflow instructions into any git repository.

Usage:
    python Golazo_Copilot.py

Run this script from anywhere within a git repository to install the Golazo
workflow instructions to that repository's .github/ directory.
"""

import sys
from pathlib import Path
import shutil


def find_repo_root(start_path: Path) -> Path | None:
    """
    Find the git repository root by traversing up from start_path.
    
    Args:
        start_path: Directory to start searching from
        
    Returns:
        Path to repository root, or None if not in a git repository
    """
    current = start_path.resolve()
    
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    
    # Check the root directory itself
    if (current / ".git").exists():
        return current
    
    return None


def get_script_directory() -> Path:
    """
    Get the directory containing this script.
    
    Returns:
        Path to the script's directory
    """
    return Path(__file__).parent.resolve()


def ensure_directory(path: Path) -> None:
    """
    Create a directory if it doesn't exist.
    
    Args:
        path: Directory path to create
    """
    path.mkdir(parents=True, exist_ok=True)


def copy_file(source: Path, destination: Path) -> bool:
    """
    Copy a file from source to destination.
    
    Args:
        source: Source file path
        destination: Destination file path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        shutil.copy2(source, destination)
        return True
    except (OSError, shutil.Error) as e:
        print(f"Error copying {source.name}: {e}", file=sys.stderr)
        return False


def install_golazo(target_root: Path) -> bool:
    """
    Install Golazo instruction files to the target repository.
    
    Args:
        target_root: Root directory of the target git repository
        
    Returns:
        True if all files installed successfully, False otherwise
    """
    script_dir = get_script_directory()
    source_github = script_dir / ".github"
    
    # Verify source files exist
    if not source_github.exists():
        print(f"Error: Source .github/ directory not found at {source_github}", file=sys.stderr)
        return False
    
    source_spine = source_github / "copilot-instructions.md"
    if not source_spine.exists():
        print(f"Error: Source copilot-instructions.md not found", file=sys.stderr)
        return False
    
    source_roles = source_github / "roles"
    if not source_roles.exists():
        print(f"Error: Source roles/ directory not found", file=sys.stderr)
        return False
    
    # Create target directories
    target_github = target_root / ".github"
    target_roles = target_github / "roles"
    
    try:
        ensure_directory(target_github)
        ensure_directory(target_roles)
    except OSError as e:
        print(f"Error creating directories: {e}", file=sys.stderr)
        return False
    
    # Track results
    files_copied = []
    errors = []
    
    # Copy spine file
    target_spine = target_github / "copilot-instructions.md"
    if copy_file(source_spine, target_spine):
        files_copied.append(target_spine)
    else:
        errors.append(source_spine.name)
    
    # Copy role files
    for role_file in source_roles.glob("*.md"):
        target_file = target_roles / role_file.name
        if copy_file(role_file, target_file):
            files_copied.append(target_file)
        else:
            errors.append(role_file.name)
    
    # Report results
    if files_copied:
        print(f"Successfully installed {len(files_copied)} files:")
        for f in files_copied:
            print(f"  ? {f.relative_to(target_root)}")
    
    if errors:
        print(f"\nFailed to copy {len(errors)} files:", file=sys.stderr)
        for name in errors:
            print(f"  ? {name}", file=sys.stderr)
        return False
    
    return True


def main() -> int:
    """
    Main entry point for the CLI.
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Find the repository root from current working directory
    cwd = Path.cwd()
    repo_root = find_repo_root(cwd)
    
    if repo_root is None:
        print("Error: Not inside a git repository.", file=sys.stderr)
        print("Please run this command from within a git repository.", file=sys.stderr)
        return 1
    
    print(f"Found git repository at: {repo_root}")
    print(f"Installing Golazo instructions...\n")
    
    if install_golazo(repo_root):
        print(f"\n? Golazo installation complete!")
        return 0
    else:
        print(f"\n? Golazo installation failed.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
