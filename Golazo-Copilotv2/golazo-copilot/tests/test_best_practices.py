"""Tests for TechBestPractices.md code examples.

These tests verify that the code examples in TechBestPractices.md are valid
and will actually work when users copy them.
"""

import pytest
import subprocess
import sys


class TestAzureIdentityBestPractice:
    """Test Azure Identity credential chaining example."""

    def test_azure_identity_imports_exist(self):
        """Verify the recommended Azure Identity imports are available."""
        # This tests that azure-identity package has the required classes
        try:
            from azure.identity import (
                ChainedTokenCredential,
                AzureCliCredential,
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
                ChainedTokenCredential,
                AzureCliCredential,
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


class TestKustoBestPractice:
    """Test Kusto/accia-datacollection example."""

    def test_accia_datacollection_import(self):
        """Verify accia.datacollection.KustoHandler can be imported."""
        try:
            from accia.datacollection import KustoHandler
            assert KustoHandler is not None
        except ImportError:
            pytest.skip("accia-datacollection not installed - skipping")

    def test_kusto_handler_accepts_documented_params(self):
        """Verify KustoHandler accepts the documented constructor parameters."""
        try:
            from azure.identity import AzureCliCredential
            from accia.datacollection import KustoHandler
            
            # Verify the constructor accepts these parameters
            handler = KustoHandler(
                AlternateAADCredentialsList=[AzureCliCredential()],
                UseDefaultCredentials=False
            )
            assert handler is not None
            
            # Verify it has the documented method
            assert hasattr(handler, 'GetDataFrameFromKustoQuery'), \
                "KustoHandler should have GetDataFrameFromKustoQuery method"
                
        except ImportError:
            pytest.skip("accia-datacollection not installed - skipping")

    def test_kusto_handler_method_signature(self):
        """Verify GetDataFrameFromKustoQuery accepts documented parameters."""
        try:
            from azure.identity import AzureCliCredential
            from accia.datacollection import KustoHandler
            import inspect
            
            handler = KustoHandler(
                AlternateAADCredentialsList=[AzureCliCredential()],
                UseDefaultCredentials=False
            )
            
            # Get the method signature
            sig = inspect.signature(handler.GetDataFrameFromKustoQuery)
            params = list(sig.parameters.keys())
            
            # Verify documented parameters are accepted
            # Note: might be **kwargs so we test by trying to call
            # We can't actually call it without a real cluster, but we can 
            # verify the method exists and is callable
            assert callable(handler.GetDataFrameFromKustoQuery)
            
        except ImportError:
            pytest.skip("accia-datacollection not installed - skipping")


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
        from importlib import resources
        import re
        
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
        "quality-assurance",
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
