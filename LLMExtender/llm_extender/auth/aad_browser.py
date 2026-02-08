"""AAD browser authentication helpers for LLM Extender.

Provides utilities for AAD device-code-flow authentication in headless
browsers. Used when ``browser_auth="aad"`` is specified on URL fetches.

Requires ``msal`` (included in the ``[browser]`` optional dependency).
"""

from __future__ import annotations

import base64
import json
import sys
from typing import Any
from urllib.parse import parse_qs, urlparse

from llm_extender.auth.base import AuthStrategy
from llm_extender.exceptions import AuthenticationError

# ---------------------------------------------------------------------------
# AAD login host patterns
# ---------------------------------------------------------------------------

_AAD_HOSTS = frozenset({
    "login.microsoftonline.com",
    "login.windows.net",
    "login.microsoft.com",
})


# ---------------------------------------------------------------------------
# Credential type detection
# ---------------------------------------------------------------------------

def is_user_credential(auth: AuthStrategy) -> bool:
    """Check whether the auth strategy represents user credentials.

    Returns ``False`` for ``ManagedIdentityAuth`` (service identity),
    ``True`` for all other strategies (user-provided credentials).

    Args:
        auth: The auth strategy to inspect.

    Returns:
        ``True`` if the credential is user-based, ``False`` for MSI.
    """
    # Import here to avoid circular dependency / optional-dep issues
    try:
        from llm_extender.auth.msi import ManagedIdentityAuth
    except ImportError:
        # If azure-identity isn't installed, it can't be MSI
        return True

    return not isinstance(auth, ManagedIdentityAuth)


# ---------------------------------------------------------------------------
# JWT decoding (claims only, no verification)
# ---------------------------------------------------------------------------

def decode_jwt_claims(token: str) -> dict[str, Any]:
    """Decode the payload claims from a JWT without signature verification.

    This is used solely to extract ``upn`` (user principal name) and
    ``tid`` (tenant ID) for AAD login flow orchestration — **not** for
    security-sensitive decisions.

    Args:
        token: A JWT string (``header.payload.signature``).

    Returns:
        The decoded payload as a dict.

    Raises:
        ValueError: If the token cannot be decoded.
    """
    try:
        payload_b64 = token.split(".")[1]
        # Add padding if needed
        padding = 4 - len(payload_b64) % 4
        if padding != 4:
            payload_b64 += "=" * padding
        payload_bytes = base64.urlsafe_b64decode(payload_b64)
        return json.loads(payload_bytes)
    except (IndexError, ValueError, json.JSONDecodeError) as exc:
        raise ValueError(f"Failed to decode JWT claims: {exc}") from exc


# ---------------------------------------------------------------------------
# AAD redirect detection
# ---------------------------------------------------------------------------

def detect_aad_redirect(url: str) -> bool:
    """Check whether a URL is an AAD login redirect.

    Args:
        url: The URL to inspect.

    Returns:
        ``True`` if the URL host is a known AAD login domain.
    """
    parsed = urlparse(url)
    return parsed.hostname in _AAD_HOSTS


def parse_aad_authorize_url(url: str) -> dict[str, str]:
    """Extract key parameters from an AAD authorize URL.

    Args:
        url: The full AAD authorize URL.

    Returns:
        A dict with ``client_id``, ``redirect_uri``, ``scope``,
        ``state``, ``tenant_id``, and ``response_type`` (where present).
    """
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)

    # Extract tenant_id from the path: /tenant-id/oauth2/...
    path_parts = [p for p in parsed.path.split("/") if p]
    tenant_id = path_parts[0] if path_parts else "common"

    return {
        "client_id": qs.get("client_id", [""])[0],
        "redirect_uri": qs.get("redirect_uri", [""])[0],
        "scope": qs.get("scope", [""])[0],
        "state": qs.get("state", [""])[0],
        "response_type": qs.get("response_type", [""])[0],
        "tenant_id": tenant_id,
    }


# ---------------------------------------------------------------------------
# MSAL device code flow
# ---------------------------------------------------------------------------

_MSAL_INSTALL_MSG = (
    "MSAL is required for browser_auth='aad'. "
    "Install it with: pip install llm-extender[browser]"
)


def _create_msal_app(tenant_id: str) -> Any:
    """Create an MSAL PublicClientApplication for device code flow.

    Uses a well-known Microsoft public client ID if the target app's
    client_id requires admin consent.

    Raises:
        AuthenticationError: If ``msal`` is not installed.
    """
    try:
        import msal  # noqa: WPS433
    except ImportError:
        raise AuthenticationError(_MSAL_INSTALL_MSG) from None

    # Use a well-known Azure CLI client_id for device code flow.
    # This avoids needing app registration for the target site.
    _AZURE_CLI_CLIENT_ID = "04b07795-a710-4e51-be09-a3fec46ee6ed"

    return msal.PublicClientApplication(
        client_id=_AZURE_CLI_CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{tenant_id}",
    )


def run_device_code_flow(
    *,
    tenant_id: str,
    scopes: list[str],
    timeout: float = 60.0,
) -> dict[str, Any]:
    """Run an MSAL device code flow and return the token response.

    Prints the device code instructions to stderr so the user can
    authenticate in their own browser.

    Args:
        tenant_id: The AAD tenant ID.
        scopes: The scopes to request (e.g. ``["https://s360.com/.default"]``).
        timeout: Timeout in seconds for the user to authenticate.

    Returns:
        The MSAL token response dict (contains ``access_token``, etc.).

    Raises:
        AuthenticationError: If the flow fails or times out.
    """
    app = _create_msal_app(tenant_id)
    flow = app.initiate_device_flow(scopes=scopes)

    if "error" in flow:
        raise AuthenticationError(
            f"Failed to initiate device code flow: {flow.get('error_description', flow['error'])}"
        )

    # Print instructions to stderr (not stdout)
    print(flow["message"], file=sys.stderr, flush=True)

    # Block until user authenticates or timeout
    result = app.acquire_token_by_device_flow(flow)

    if "error" in result:
        raise AuthenticationError(
            f"AAD device code authentication failed: "
            f"{result.get('error_description', result['error'])}"
        )

    return result
