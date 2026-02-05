"""
Test fixtures and configuration for S360 Client tests.
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from s360_client.config import S360Config


@pytest.fixture
def mock_token() -> str:
    """A mock JWT token for testing."""
    return "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.mock_signature"


@pytest.fixture
def sample_user_info() -> dict:
    """Sample Microsoft Graph user response."""
    return {
        "displayName": "Test User",
        "userPrincipalName": "testuser@microsoft.com",
        "mail": "testuser@microsoft.com",
    }


@pytest.fixture
def sample_eta_history() -> list[dict]:
    """Sample ETA history API response."""
    return [
        {
            "id": "item-1",
            "eta": "2026-03-01T00:00:00Z",
            "status": "InProgress",
            "notes": "Working on it",
            "createdAt": "2026-02-01T10:00:00Z",
        },
        {
            "id": "item-2",
            "eta": "2026-02-15T00:00:00Z",
            "status": "Complete",
            "notes": "Done",
            "createdAt": "2026-01-15T10:00:00Z",
        },
    ]


@pytest.fixture
def temp_cache_dir(tmp_path: Path) -> Path:
    """Temporary cache directory for testing."""
    cache_dir = tmp_path / "s360_cache"
    cache_dir.mkdir(parents=True)
    return cache_dir


@pytest.fixture
def test_config(temp_cache_dir: Path) -> S360Config:
    """Test configuration with temp cache directory."""
    return S360Config(
        cache_directory=temp_cache_dir,
        timeout_seconds=5,
        cache_expiry_minutes=60,
    )


@pytest.fixture
def mock_credential():
    """Mock AzureCliCredential."""
    with patch("s360_client.auth.AzureCliCredential") as mock:
        credential_instance = MagicMock()
        mock.return_value = credential_instance
        
        # Default: return a valid token
        token = MagicMock()
        token.token = "mock_bearer_token"
        credential_instance.get_token.return_value = token
        
        yield credential_instance
