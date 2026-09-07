"""Tests for GCP-0066: changelog maintenance and version-first sequencing."""

import re
from importlib import resources


def _read_role(role_name: str) -> str:
    """Read a role file from package defaults."""
    role_files = resources.files("golazo_copilot.roles.defaults")
    return role_files.joinpath(f"{role_name}.md").read_text(encoding="utf-8")


class TestBuilderChangelogPolicy:
    """AC1: Builder requires changelog maintenance at end of README."""

    def test_builder_requires_changelog_maintenance(self):
        content = _read_role("builder")
        responsibilities = re.search(r"## Responsibilities\n(.*?)(?=\n## )", content, re.DOTALL)
        assert responsibilities, "Builder missing Responsibilities section"

        text = responsibilities.group(1).lower()
        assert "changelog" in text and "readme.md" in text, (
            "Expected Builder role to require changelog maintenance in README.md."
        )

    def test_builder_requires_end_of_readme_placement(self):
        content = _read_role("builder")
        text = content.lower()
        assert "end of `readme.md`" in text or "end of readme.md" in text, (
            "Expected Builder role to require changelog maintenance at end of README."
        )


class TestVersionBeforeChangelogPolicy:
    """AC2: Version must be updated before changelog maintenance."""

    def test_builder_defines_pyproject_version_source(self):
        content = _read_role("builder")
        text = content.lower()
        assert "pyproject.toml" in text and "version" in text, (
            "Expected Builder role to define pyproject.toml as canonical version source."
        )

    def test_builder_requires_version_before_changelog(self):
        content = _read_role("builder")
        text = content.lower()
        version_update = text.index("after updating `pyproject.toml`")
        changelog_update = text.index("matching newest-first release entry")
        assert changelog_update < version_update, (
            "Expected Builder to require version update before changelog maintenance."
        )
