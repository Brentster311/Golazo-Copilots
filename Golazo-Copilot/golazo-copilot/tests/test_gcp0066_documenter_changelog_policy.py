"""Tests for GCP-0066: changelog maintenance and version-first sequencing."""

import re
from importlib import resources


def _read_role(role_name: str) -> str:
    """Read a role file from package defaults."""
    role_files = resources.files("golazo_copilot.roles.defaults")
    return role_files.joinpath(f"{role_name}.md").read_text(encoding="utf-8")


class TestDocumenterChangelogPolicy:
    """AC1: Documenter requires changelog maintenance at end of README."""

    def test_documenter_requires_changelog_maintenance(self):
        content = _read_role("documenter")
        responsibilities = re.search(r"## Responsibilities\n(.*?)(?=\n## )", content, re.DOTALL)
        assert responsibilities, "Documenter missing Responsibilities section"

        text = responsibilities.group(1).lower()
        assert "changelog" in text and "readme.md" in text, (
            "Expected Documenter role to require changelog maintenance in README.md."
        )

    def test_documenter_requires_end_of_readme_placement(self):
        content = _read_role("documenter")
        text = content.lower()
        assert "end of `readme.md`" in text or "end of readme.md" in text, (
            "Expected Documenter role to require changelog maintenance at end of README."
        )


class TestVersionBeforeChangelogPolicy:
    """AC2: Version must be updated before changelog maintenance."""

    def test_builder_defines_pyproject_version_source(self):
        content = _read_role("builder")
        text = content.lower()
        assert "pyproject.toml" in text and "version" in text, (
            "Expected Builder role to define pyproject.toml as canonical version source."
        )

    def test_documenter_requires_version_before_changelog(self):
        content = _read_role("documenter")
        text = content.lower()
        assert "version" in text and "before" in text and "changelog" in text, (
            "Expected version update requirement before changelog maintenance."
        )
