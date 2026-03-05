"""Tests for TechBestPractices.md code examples.

These tests verify that the code examples in TechBestPractices.md are valid
and will actually work when users copy them.
"""


import pytest


class TestAzureIdentityBestPractice:
    """Test Azure Identity credential chaining example."""

    def test_azure_identity_imports_exist(self):
        """Verify the recommended Azure Identity imports are available."""
        # This tests that azure-identity package has the required classes
        try:
            from azure.identity import (
                AzureCliCredential,
                ChainedTokenCredential,
                ManagedIdentityCredential,
            )
            assert ChainedTokenCredential is not None
            assert AzureCliCredential is not None
            assert ManagedIdentityCredential is not None
        except ImportError:
            pytest.skip("azure-identity not installed - skipping")

    def test_chained_credential_construction(self):
        """Verify the recommended credential chain can be constructed."""
        try:
            from azure.identity import (
                AzureCliCredential,
                ChainedTokenCredential,
                ManagedIdentityCredential,
            )
            
            # This should not raise - just constructing the chain
            credential = ChainedTokenCredential(
                AzureCliCredential(),
                ManagedIdentityCredential()
            )
            
            assert credential is not None
            # Verify it has the expected interface
            assert hasattr(credential, 'get_token')
        except ImportError:
            pytest.skip("azure-identity not installed - skipping")

    def test_default_credential_also_exists(self):
        """Verify DefaultAzureCredential exists (for comparison in docs)."""
        try:
            from azure.identity import DefaultAzureCredential
            assert DefaultAzureCredential is not None
        except ImportError:
            pytest.skip("azure-identity not installed - skipping")


class TestBestPracticesFileExists:
    """Verify TechBestPractices.md is included in package."""

    def test_techbestpractices_in_package(self):
        """TechBestPractices.md should be in the roles defaults."""
        from importlib import resources
        
        role_files = resources.files("golazo_copilot.roles.defaults")
        bp_file = role_files.joinpath("TechBestPractices.md")
        
        content = bp_file.read_text(encoding="utf-8")
        
        # Verify key content is present
        assert "Azure Identity" in content
        assert "ChainedTokenCredential" in content
        assert "Kusto" in content
        assert "accia.datacollection" in content
        assert "KustoHandler" in content
        assert "GetDataFrameFromKustoQuery" in content

    def test_code_examples_are_valid_python(self):
        """Extract and validate Python code blocks from TechBestPractices.md."""
        import re
        from importlib import resources
        
        role_files = resources.files("golazo_copilot.roles.defaults")
        bp_file = role_files.joinpath("TechBestPractices.md")
        content = bp_file.read_text(encoding="utf-8")
        
        # Extract all Python code blocks
        code_blocks = re.findall(r'```python\n(.*?)```', content, re.DOTALL)
        
        assert len(code_blocks) >= 2, "Expected at least 2 Python code blocks"
        
        # Verify each is valid Python syntax (compile check)
        for i, code in enumerate(code_blocks):
            try:
                compile(code, f"<code_block_{i}>", "exec")
            except SyntaxError as e:
                pytest.fail(f"Code block {i} has invalid Python syntax: {e}\n\nCode:\n{code}")


class TestCapabilityRegistryInRoles:
    """GCP-0039: Verify capability registry sections in role files."""

    ROLES_WITH_REGISTRY = [
        "architect",
        "developer",
        "refactor-expert",
        "retrospective",
    ]

    @pytest.mark.parametrize("role", ROLES_WITH_REGISTRY)
    def test_role_contains_capability_registry_section(self, role):
        """Each role file must contain a Capability Registry section."""
        from importlib import resources
        role_files = resources.files("golazo_copilot.roles.defaults")
        content = role_files.joinpath(f"{role}.md").read_text(encoding="utf-8")
        assert "### Capability Registry" in content, f"{role}.md missing Capability Registry section"

    @pytest.mark.parametrize("role", ROLES_WITH_REGISTRY)
    def test_role_uses_conditional_phrasing(self, role):
        """Each role's registry section must be conditional on capabilities.yaml."""
        from importlib import resources
        role_files = resources.files("golazo_copilot.roles.defaults")
        content = role_files.joinpath(f"{role}.md").read_text(encoding="utf-8")
        assert "capabilities.yaml" in content, f"{role}.md missing conditional capabilities.yaml reference"


class TestSpineCapabilityRegistryMention:
    """GCP-0041: Verify bootstrap-instructions.md (spine) mentions capability registry."""

    @staticmethod
    def _read_spine() -> str:
        from importlib import resources
        files_pkg = resources.files("golazo_copilot")
        return files_pkg.joinpath("bootstrap-instructions.md").read_text(encoding="utf-8")

    def test_spine_mentions_golazo_capabilities(self):
        """TC1: Spine contains golazo_capabilities mention."""
        content = self._read_spine()
        assert "golazo_capabilities" in content, "Spine missing golazo_capabilities mention"

    def test_spine_uses_conditional_phrasing(self):
        """TC2: Spine mention uses conditional phrasing about capabilities.yaml."""
        content = self._read_spine()
        assert "capabilities.yaml" in content, "Spine missing conditional capabilities.yaml reference"

    def test_spine_capability_section_is_brief(self):
        """TC3: Capability Registry section is <= 10 lines."""
        content = self._read_spine()
        in_section = False
        section_lines = []
        for line in content.splitlines():
            if "Capability Registry" in line and line.startswith("#"):
                in_section = True
                section_lines.append(line)
                continue
            if in_section:
                if line.startswith("#"):
                    break
                section_lines.append(line)
        assert len(section_lines) > 0, "Spine missing Capability Registry section heading"
        assert len(section_lines) <= 10, f"Section is {len(section_lines)} lines, expected <= 10"
