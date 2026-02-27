"""Tests for browser_auth='aad' support — maps to LLM-0008 test cases."""

from __future__ import annotations

import base64
import json
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from llm_extender.exceptions import AuthenticationError, ProviderError


# ===========================================================================
# TC-1 / TC-2: MSI auth rejected
# ===========================================================================

class TestMSIGuard:
    def test_msi_auth_rejected_sync(self) -> None:
        """TC-1: browser_auth='aad' with ManagedIdentityAuth raises AuthenticationError."""
        from llm_extender.auth.msi import ManagedIdentityAuth
        from llm_extender.auth.aad_browser import is_user_credential

        mock_msi = MagicMock(spec=ManagedIdentityAuth)
        mock_msi.__class__ = ManagedIdentityAuth
        assert is_user_credential(mock_msi) is False

    @pytest.mark.asyncio
    async def test_msi_auth_rejected_async(self) -> None:
        """TC-2: browser_auth='aad' with MSI raises AuthenticationError (async path)."""
        from llm_extender.auth.msi import ManagedIdentityAuth
        from llm_extender.auth.aad_browser import is_user_credential

        mock_msi = MagicMock(spec=ManagedIdentityAuth)
        mock_msi.__class__ = ManagedIdentityAuth
        assert is_user_credential(mock_msi) is False


# ===========================================================================
# TC-3: browser_auth=None is default
# ===========================================================================

class TestBrowserAuthDefault:
    def test_default_is_none(self) -> None:
        """TC-3: fetch_url's browser_auth defaults to None."""
        import inspect
        from llm_extender.url_fetcher import fetch_url

        sig = inspect.signature(fetch_url)
        assert sig.parameters["browser_auth"].default is None


# ===========================================================================
# TC-4 / TC-5: client passes browser_auth through
# ===========================================================================

class TestClientBrowserAuthPassthrough:
    def test_complete_with_url_passes_browser_auth(self) -> None:
        """TC-4: complete_with_url forwards browser_auth to fetch_url."""
        from llm_extender import LLMClient, LLMConfig

        config = LLMConfig(provider="openai", model="test", api_key="fake")
        client = LLMClient(config)
        client._provider = MagicMock()
        client._provider.complete.return_value = "Summary"

        with patch("llm_extender.client.fetch_url") as mock_fetch:
            mock_fetch.return_value = "Fetched content"
            client.complete_with_url(
                prompt="Summarize",
                url="https://example.com",
                render_js=True,
                browser_auth="aad",
            )
            call_kwargs = mock_fetch.call_args.kwargs
            assert call_kwargs.get("browser_auth") == "aad"

    @pytest.mark.asyncio
    async def test_acomplete_with_url_passes_browser_auth(self) -> None:
        """TC-5: acomplete_with_url forwards browser_auth to afetch_url."""
        from llm_extender import LLMClient, LLMConfig

        config = LLMConfig(provider="openai", model="test", api_key="fake")
        client = LLMClient(config)
        client._provider = MagicMock()
        client._provider.acomplete = AsyncMock(return_value="Summary")

        with patch("llm_extender.client.afetch_url", new_callable=AsyncMock) as mock_afetch:
            mock_afetch.return_value = "Fetched content"
            await client.acomplete_with_url(
                prompt="Summarize",
                url="https://example.com",
                render_js=True,
                browser_auth="aad",
            )
            call_kwargs = mock_afetch.call_args.kwargs
            assert call_kwargs.get("browser_auth") == "aad"


# ===========================================================================
# TC-6 / TC-7: is_user_credential
# ===========================================================================

class TestIsUserCredential:
    def test_returns_true_for_env_var_auth(self) -> None:
        """TC-6: EnvVarAuth is considered user credential."""
        from llm_extender.auth.aad_browser import is_user_credential
        from llm_extender.auth.env_var import EnvVarAuth

        with patch.dict("os.environ", {"TEST_KEY": "value"}):
            auth = EnvVarAuth("TEST_KEY")
        assert is_user_credential(auth) is True

    def test_returns_true_for_callback_auth(self) -> None:
        """TC-6: CallbackAuth is considered user credential."""
        from llm_extender.auth.aad_browser import is_user_credential
        from llm_extender.auth.callback import CallbackAuth

        auth = CallbackAuth(callback=lambda: "token")
        assert is_user_credential(auth) is True

    def test_returns_false_for_msi(self) -> None:
        """TC-7: ManagedIdentityAuth is not a user credential."""
        from llm_extender.auth.aad_browser import is_user_credential
        from llm_extender.auth.msi import ManagedIdentityAuth

        mock_msi = MagicMock(spec=ManagedIdentityAuth)
        mock_msi.__class__ = ManagedIdentityAuth
        assert is_user_credential(mock_msi) is False


# ===========================================================================
# TC-8: decode_jwt_claims
# ===========================================================================

class TestDecodeJwtClaims:
    def _make_jwt(self, claims: dict) -> str:
        """Build a fake JWT with the given payload claims."""
        header = base64.urlsafe_b64encode(b'{"alg":"none"}').rstrip(b"=")
        payload = base64.urlsafe_b64encode(
            json.dumps(claims).encode()
        ).rstrip(b"=")
        sig = base64.urlsafe_b64encode(b"sig").rstrip(b"=")
        return f"{header.decode()}.{payload.decode()}.{sig.decode()}"

    def test_extracts_upn_and_tid(self) -> None:
        """TC-8: decode_jwt_claims extracts upn and tid from JWT payload."""
        from llm_extender.auth.aad_browser import decode_jwt_claims

        token = self._make_jwt({
            "upn": "user@contoso.com",
            "tid": "tenant-id-123",
            "aud": "some-audience",
        })
        claims = decode_jwt_claims(token)
        assert claims["upn"] == "user@contoso.com"
        assert claims["tid"] == "tenant-id-123"

    def test_handles_padded_base64(self) -> None:
        """TC-8: decode_jwt_claims handles missing base64 padding."""
        from llm_extender.auth.aad_browser import decode_jwt_claims

        claims_data = {"upn": "a@b.com", "tid": "t1"}
        token = self._make_jwt(claims_data)
        result = decode_jwt_claims(token)
        assert result["upn"] == "a@b.com"


# ===========================================================================
# TC-9: detect_aad_redirect
# ===========================================================================

class TestDetectAadRedirect:
    def test_login_microsoftonline_detected(self) -> None:
        """TC-9: login.microsoftonline.com URLs detected as AAD."""
        from llm_extender.auth.aad_browser import detect_aad_redirect

        assert detect_aad_redirect(
            "https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id=abc"
        ) is True

    def test_non_aad_url_not_detected(self) -> None:
        """TC-9: Non-AAD URLs return False."""
        from llm_extender.auth.aad_browser import detect_aad_redirect

        assert detect_aad_redirect("https://example.com/page") is False
        assert detect_aad_redirect("https://vnext.s360.msftcloudes.com") is False

    def test_login_windows_net_detected(self) -> None:
        """TC-9: login.windows.net (legacy AAD) also detected."""
        from llm_extender.auth.aad_browser import detect_aad_redirect

        assert detect_aad_redirect(
            "https://login.windows.net/tenant-id/oauth2/authorize"
        ) is True


# ===========================================================================
# TC-10: parse_aad_authorize_url
# ===========================================================================

class TestParseAadAuthorizeUrl:
    def test_extracts_params(self) -> None:
        """TC-10: parse_aad_authorize_url extracts client_id, scope, etc."""
        from llm_extender.auth.aad_browser import parse_aad_authorize_url

        url = (
            "https://login.microsoftonline.com/tenant-123/oauth2/v2.0/authorize"
            "?client_id=app-id-456"
            "&redirect_uri=https%3A%2F%2Fexample.com%2Fcallback"
            "&scope=openid%20profile%20user.read"
            "&state=abc123"
            "&response_type=code"
        )
        params = parse_aad_authorize_url(url)
        assert params["client_id"] == "app-id-456"
        assert params["redirect_uri"] == "https://example.com/callback"
        assert "openid" in params["scope"]
        assert params["state"] == "abc123"
        assert params["tenant_id"] == "tenant-123"


# ===========================================================================
# TC-11 / TC-12: device code flow
# ===========================================================================

class TestDeviceCodeFlow:
    def test_initiate_called_with_scope(self) -> None:
        """TC-11: MSAL device code flow initiated with correct scope."""
        from llm_extender.auth.aad_browser import run_device_code_flow

        mock_app = MagicMock()
        mock_flow = {
            "user_code": "ABCD1234",
            "message": "Go to https://microsoft.com/devicelogin and enter code ABCD1234",
        }
        mock_app.initiate_device_flow.return_value = mock_flow
        mock_app.acquire_token_by_device_flow.return_value = {
            "access_token": "fresh-token",
            "id_token": "id-token",
        }

        with patch("llm_extender.auth.aad_browser._create_msal_app", return_value=mock_app):
            result = run_device_code_flow(
                tenant_id="tenant-123",
                scopes=["https://s360.microsoft.com/.default"],
            )

        mock_app.initiate_device_flow.assert_called_once_with(
            scopes=["https://s360.microsoft.com/.default"]
        )
        assert result["access_token"] == "fresh-token"

    def test_device_code_message_printed_to_stderr(self, capsys) -> None:
        """TC-12: Device code instructions printed to stderr."""
        from llm_extender.auth.aad_browser import run_device_code_flow

        mock_app = MagicMock()
        device_msg = "To sign in, visit https://microsoft.com/devicelogin and enter code TEST1234"
        mock_flow = {
            "user_code": "TEST1234",
            "message": device_msg,
        }
        mock_app.initiate_device_flow.return_value = mock_flow
        mock_app.acquire_token_by_device_flow.return_value = {
            "access_token": "tok",
        }

        with patch("llm_extender.auth.aad_browser._create_msal_app", return_value=mock_app):
            run_device_code_flow(tenant_id="t", scopes=["s"])

        captured = capsys.readouterr()
        assert device_msg in captured.err

    def test_device_code_flow_error_raises(self) -> None:
        """TC-11: MSAL error in device code flow raises AuthenticationError."""
        from llm_extender.auth.aad_browser import run_device_code_flow

        mock_app = MagicMock()
        mock_flow = {"user_code": "X", "message": "msg"}
        mock_app.initiate_device_flow.return_value = mock_flow
        mock_app.acquire_token_by_device_flow.return_value = {
            "error": "authorization_declined",
            "error_description": "User declined",
        }

        with patch("llm_extender.auth.aad_browser._create_msal_app", return_value=mock_app):
            with pytest.raises(AuthenticationError, match="User declined"):
                run_device_code_flow(tenant_id="t", scopes=["s"])


# ===========================================================================
# TC-13: browser_auth requires render_js=True
# ===========================================================================

class TestBrowserAuthRequiresRenderJs:
    def test_raises_without_render_js(self) -> None:
        """TC-13: browser_auth='aad' without render_js=True raises ProviderError."""
        from llm_extender.url_fetcher import fetch_url

        mock_auth = MagicMock()
        mock_auth.resolve.return_value = "token"

        with pytest.raises(ProviderError, match="render_js=True"):
            fetch_url(
                "https://example.com",
                auth=mock_auth,
                render_js=False,
                browser_auth="aad",
            )

    @pytest.mark.asyncio
    async def test_async_raises_without_render_js(self) -> None:
        """TC-13: async variant also requires render_js=True."""
        from llm_extender.url_fetcher import afetch_url

        mock_auth = MagicMock()
        mock_auth.aresolve = AsyncMock(return_value="token")

        with pytest.raises(ProviderError, match="render_js=True"):
            await afetch_url(
                "https://example.com",
                auth=mock_auth,
                render_js=False,
                browser_auth="aad",
            )


# ===========================================================================
# TC-14: invalid browser_auth value
# ===========================================================================

class TestInvalidBrowserAuth:
    def test_invalid_value_raises(self) -> None:
        """TC-14: Unsupported browser_auth value raises ProviderError."""
        from llm_extender.url_fetcher import fetch_url

        with pytest.raises(ProviderError, match="Unsupported browser_auth"):
            fetch_url(
                "https://example.com",
                render_js=True,
                browser_auth="invalid_value",
            )


# ===========================================================================
# TC-15: Non-MSI auth allowed
# ===========================================================================

class TestNonMSIAllowed:
    def test_env_var_auth_allowed(self) -> None:
        """TC-15: EnvVarAuth is accepted by the MSI guard."""
        from llm_extender.auth.aad_browser import is_user_credential
        from llm_extender.auth.env_var import EnvVarAuth

        with patch.dict("os.environ", {"MY_KEY": "val"}):
            auth = EnvVarAuth("MY_KEY")
        assert is_user_credential(auth) is True


# ===========================================================================
# TC-16: Docstrings mention browser_auth
# ===========================================================================

class TestBrowserAuthDocstrings:
    def test_fetch_url_docstring(self) -> None:
        """TC-16: fetch_url docstring documents browser_auth."""
        from llm_extender.url_fetcher import fetch_url
        assert "browser_auth" in fetch_url.__doc__

    def test_afetch_url_docstring(self) -> None:
        """TC-16: afetch_url docstring documents browser_auth."""
        from llm_extender.url_fetcher import afetch_url
        assert "browser_auth" in afetch_url.__doc__
