"""Tests for accia-s360 package structure and imports."""
import pytest


class TestPackageStructure:
    """Test package is properly structured and importable."""

    def test_package_importable(self):
        """TC-001: Verify package can be imported after installation."""
        import accia_s360
        assert accia_s360 is not None

    def test_public_api_exports_s360client(self):
        """TC-002: Verify S360Client is exported from package root."""
        from accia_s360 import S360Client
        assert S360Client is not None

    def test_public_api_exports_exceptions(self):
        """TC-002b: Verify exceptions are exported from package root."""
        from accia_s360 import S360Error, S360AuthError, S360ApiError
        assert S360Error is not None
        assert S360AuthError is not None
        assert S360ApiError is not None

    def test_public_api_exports_models(self):
        """TC-002c: Verify models are exported from package root."""
        from accia_s360 import UserInfo
        assert UserInfo is not None

    def test_version_defined(self):
        """TC-003: Verify package version is accessible."""
        import accia_s360
        assert hasattr(accia_s360, '__version__')
        assert accia_s360.__version__ == '0.1.0'

    def test_all_exports_defined(self):
        """TC-003b: Verify __all__ is defined and contains expected exports."""
        import accia_s360
        assert hasattr(accia_s360, '__all__')
        expected = ['S360Client', 'S360Error', 'S360AuthError', 'S360ApiError']
        for item in expected:
            assert item in accia_s360.__all__, f"Missing {item} in __all__"


class TestBackwardCompatibility:
    """Test backward compatibility with existing functionality."""

    def test_client_class_exists(self):
        """TC-004: Verify S360Client can be instantiated type exists."""
        from accia_s360 import S360Client
        # Just verify the class exists, not that it can connect
        assert callable(S360Client)

    def test_endpoint_methods_exist(self):
        """TC-005: Verify all expected endpoint methods are available on class."""
        from accia_s360 import S360Client
        
        expected_methods = [
            'get_current_user',
            'get_action_items_grid',
            'get_default_landing_view',
            'get_all_action_item_metadata',
        ]
        
        for method in expected_methods:
            assert hasattr(S360Client, method), f"Missing method: {method}"


class TestAuthentication:
    """Test authentication behavior."""

    def test_auth_module_importable(self):
        """TC-006: Verify auth module is accessible."""
        from accia_s360 import auth
        assert auth is not None

    def test_s360auth_class_exists(self):
        """TC-006b: Verify S360Auth class exists."""
        from accia_s360.auth import S360Auth
        assert S360Auth is not None


class TestExceptionHierarchy:
    """Test exception classes are properly defined."""

    def test_s360error_is_exception(self):
        """Verify S360Error inherits from Exception."""
        from accia_s360 import S360Error
        assert issubclass(S360Error, Exception)

    def test_s360autherror_inherits_s360error(self):
        """Verify S360AuthError inherits from S360Error."""
        from accia_s360 import S360Error, S360AuthError
        assert issubclass(S360AuthError, S360Error)

    def test_s360apierror_inherits_s360error(self):
        """Verify S360ApiError inherits from S360Error."""
        from accia_s360 import S360Error, S360ApiError
        assert issubclass(S360ApiError, S360Error)
