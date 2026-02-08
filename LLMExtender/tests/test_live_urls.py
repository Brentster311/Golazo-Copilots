"""Live integration tests for URL fetcher against real URLs.

These tests require network access and (for some) valid Azure CLI credentials.
Run with:  pytest -m live
Skip with: pytest -m "not live"
"""

from __future__ import annotations

import pytest

from llm_extender import AzureChainedAuth, LLMClient, LLMConfig
from llm_extender.exceptions import ProviderError
from llm_extender.url_fetcher import fetch_url

# All tests in this module require network + credentials
pytestmark = pytest.mark.live

# ---------------------------------------------------------------------------
# Shared config — assumes Azure CLI logged in and gpt-4 deployment exists
# ---------------------------------------------------------------------------

_LLM_CONFIG = LLMConfig(
    provider="azure_openai",
    model="gpt-4o",
    base_url="https://open-ai-poc.openai.azure.com",
    deployment="gpt-4",
    api_version="2024-12-01-preview",
)


# ===========================================================================
# moderntesting.org — public, server-rendered, no auth needed
# ===========================================================================

class TestModernTestingOrg:
    """Live tests against https://www.moderntesting.org/ (public page)."""

    def test_fetch_returns_content(self) -> None:
        """fetch_url retrieves readable text from a public HTML page."""
        text = fetch_url("https://www.moderntesting.org/", max_length=10_000)
        # The page should contain Modern Testing content
        assert len(text) > 100
        assert "modern testing" in text.lower() or "quality" in text.lower()

    def test_complete_with_url_summarizes(self) -> None:
        """complete_with_url produces an LLM summary grounded in page content."""
        auth = AzureChainedAuth()
        client = LLMClient(_LLM_CONFIG, auth=auth)
        result = client.complete_with_url(
            prompt="Summarize this page in 3-5 bullet points",
            url="https://www.moderntesting.org/",
        )
        # LLM should return a non-trivial summary mentioning testing
        assert len(result) > 50
        assert "testing" in result.lower() or "quality" in result.lower()


# ===========================================================================
# aka.ms/msw — redirects to SharePoint (requires auth, SPA)
# ===========================================================================

class TestAkaMsMsw:
    """Live tests against https://aka.ms/msw (SharePoint — SPA behind Azure AD)."""

    def test_fetch_without_auth_raises_401(self) -> None:
        """SharePoint returns 401 when no auth is provided."""
        with pytest.raises(ProviderError, match="401"):
            fetch_url("https://aka.ms/msw")

    def test_fetch_with_sharepoint_auth_still_fails(self) -> None:
        """SharePoint does not accept Bearer tokens for HTML pages.

        Even with a valid SharePoint-scoped token, the root page returns
        401 because SharePoint web pages require browser-based SAML/cookie
        auth, not Bearer tokens via GET.  This documents a known limitation
        that LLM-0007 (client-side rendering) aims to address.
        """
        url_auth = AzureChainedAuth(
            scope="https://microsoft.sharepoint.com/.default"
        )
        with pytest.raises(ProviderError, match="40[13]"):
            fetch_url("https://aka.ms/msw", auth=url_auth)


# ===========================================================================
# aka.ms/s360 — redirects to Service360 (SPA behind Azure AD)
# ===========================================================================

class TestAkaMsS360:
    """Live tests against https://aka.ms/s360 (Service360 — SPA behind Azure AD)."""

    def test_fetch_without_auth_raises_401(self) -> None:
        """S360 returns 401 when no auth is provided."""
        with pytest.raises(ProviderError, match="401"):
            fetch_url("https://aka.ms/s360")

    def test_fetch_with_s360_auth_returns_403_or_spa_shell(self) -> None:
        """S360 accepts the token but returns 403 or an empty SPA shell.

        The resource_id scope gets past the 401 but S360 either rejects
        with 403 or returns a JS-only shell.  This documents a known
        limitation that LLM-0007 (client-side rendering) aims to address.
        """
        url_auth = AzureChainedAuth(
            scope="1b2fb937-b01b-4695-b023-f9c67b16b837/.default"
        )
        # Could be 403, or could succeed with empty SPA shell
        try:
            text = fetch_url("https://aka.ms/s360", auth=url_auth)
            # If it succeeds, the content should be minimal (SPA shell)
            # A real page would have >500 chars of content
            assert len(text) < 2000, (
                "Unexpectedly large content — S360 may have become "
                "server-rendered (update this test)"
            )
        except ProviderError as exc:
            assert "403" in str(exc) or "401" in str(exc)
