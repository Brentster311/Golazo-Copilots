"""Debug script for AAD browser auth flow against aka.ms/s360."""
import sys

from llm_extender.url_fetcher import _get_sync_playwright
from llm_extender.auth.aad_browser import (
    detect_aad_redirect,
    parse_aad_authorize_url,
    run_device_code_flow,
)

# Step 1: Navigate without auth and check the AAD redirect
print("Step 1: Navigating to aka.ms/s360 without Bearer token...", flush=True)
launcher = _get_sync_playwright()
with launcher() as pw:
    browser = pw.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://aka.ms/s360", timeout=30000)
    page.wait_for_load_state("domcontentloaded", timeout=30000)
    final_url = page.url
    is_aad = detect_aad_redirect(final_url)
    print(f"Final URL: {final_url}", flush=True)
    print(f"Is AAD redirect: {is_aad}", flush=True)

    if is_aad:
        params = parse_aad_authorize_url(final_url)
        tenant = params.get("tenant_id", "common")
        client_id = params.get("client_id", "")
        raw_scope = params.get("scope", "")
        print(f"Tenant: {tenant}", flush=True)
        print(f"Client ID: {client_id}", flush=True)
        print(f"Raw scope: {raw_scope}", flush=True)

        # Filter reserved scopes
        _RESERVED = {"openid", "profile", "offline_access", "email"}
        scopes = [s for s in raw_scope.split() if s and s not in _RESERVED]
        if not scopes and client_id:
            scopes = [f"{client_id}/.default"]
        print(f"Effective scopes: {scopes}", flush=True)

        # Step 2: Try device code flow
        print("Step 2: Initiating device code flow...", flush=True)
        print("(Check stderr for the device code instructions)", flush=True)
        result = run_device_code_flow(
            tenant_id=tenant,
            scopes=scopes,
            client_id=client_id or None,
            timeout=120.0,
        )
        print(f"Token keys: {list(result.keys())}", flush=True)
        print("SUCCESS - got token!", flush=True)
    else:
        body = page.inner_text("body")[:500]
        print(f"Not an AAD redirect. Body: {body}", flush=True)

    browser.close()
print("Done.", flush=True)
