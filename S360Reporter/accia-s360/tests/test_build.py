"""Tests for pyproject.toml configuration."""
import pytest
from pathlib import Path


class TestDependencies:
    """Test package dependencies are properly declared."""

    def test_dependencies_in_pyproject(self):
        """TC-010: Verify required dependencies are listed in pyproject.toml."""
        try:
            import tomllib
        except ImportError:
            import tomli as tomllib
        
        pyproject_path = Path(__file__).parent.parent / 'pyproject.toml'
        
        with open(pyproject_path, 'rb') as f:
            config = tomllib.load(f)
        
        deps = config['project']['dependencies']
        deps_str = ' '.join(deps)
        
        assert 'azure-identity' in deps_str, "Missing azure-identity dependency"
        assert 'requests' in deps_str, "Missing requests dependency"

    def test_python_version_requirement(self):
        """Verify Python version requirement is set."""
        try:
            import tomllib
        except ImportError:
            import tomli as tomllib
        
        pyproject_path = Path(__file__).parent.parent / 'pyproject.toml'
        
        with open(pyproject_path, 'rb') as f:
            config = tomllib.load(f)
        
        requires_python = config['project']['requires-python']
        assert '3.10' in requires_python, "Should require Python 3.10+"

    def test_package_name_correct(self):
        """Verify package name is accia-s360."""
        try:
            import tomllib
        except ImportError:
            import tomli as tomllib
        
        pyproject_path = Path(__file__).parent.parent / 'pyproject.toml'
        
        with open(pyproject_path, 'rb') as f:
            config = tomllib.load(f)
        
        name = config['project']['name']
        assert name == 'accia-s360', f"Expected 'accia-s360', got '{name}'"
