"""Use LLM Extender to fetch and summarize aka.ms/s360.

S360 requires a managed/compliant device (Conditional Access policy).
Playwright's fresh browser instances have no device identity, so we:
  1. Launch Edge with --remote-debugging-port using the user's real profile
  2. Connect Playwright via CDP to that browser
  3. Navigate to S360 (SSO + device compliance just works)
  4. Extract page text and send to the LLM
"""

import os
import subprocess
import sys
import time

from playwright.sync_api import sync_playwright

from llm_extender import AzureChainedAuth, LLMClient, LLMConfig
from llm_extender.url_fetcher import _build_context_prompt

URL = "https://aka.ms/s360"
MAX_LENGTH = 50_000
CDP_PORT = 9223

# --- Step 1: Launch Edge with remote debugging using user's profile ---
edge_path = (
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
)
if not os.path.exists(edge_path):
    edge_path = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"

user_data = os.path.expandvars(
    r"%LOCALAPPDATA%\Microsoft\Edge\User Data"
)

# Edge ignores --remote-debugging-port when already running.
# Close existing Edge, then relaunch with debugging enabled.
print("Closing existing Edge instances (they will be restored)...",
      file=sys.stderr, flush=True)
subprocess.run(["taskkill", "/F", "/IM", "msedge.exe"],
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(3)

print("Launching Edge with your profile (remote debugging)...",
      file=sys.stderr, flush=True)

edge_proc = subprocess.Popen([
    edge_path,
    f"--remote-debugging-port={CDP_PORT}",
    f"--user-data-dir={user_data}",
    "--no-first-run",
    "--restore-last-session",
    URL,
])

# Give Edge a moment to start the CDP server
time.sleep(5)

# --- Step 2: Connect Playwright via CDP and extract content ---
with sync_playwright() as pw:
    try:
        browser = pw.chromium.connect_over_cdp(f"http://127.0.0.1:{CDP_PORT}")
    except Exception as exc:
        print(f"Could not connect to Edge via CDP: {exc}", file=sys.stderr)
        print("Make sure Edge is not blocking remote debugging.", file=sys.stderr)
        edge_proc.terminate()
        sys.exit(1)

    # Find the S360 tab (or the most recent tab)
    contexts = browser.contexts
    page = None
    for ctx in contexts:
        for p in ctx.pages:
            if "s360" in p.url.lower() or "msftcloudes" in p.url.lower():
                page = p
                break
        if page:
            break

    if page is None:
        # Fallback: use the last page of the first context
        if contexts and contexts[0].pages:
            page = contexts[0].pages[-1]
            page.goto(URL, timeout=60_000)
        else:
            print("No browser tabs found.", file=sys.stderr)
            browser.close()
            edge_proc.terminate()
            sys.exit(1)

    # Wait for AAD login to complete (user may need to interact)
    print("Waiting for S360 to load (sign in if prompted)...",
          file=sys.stderr, flush=True)
    for i in range(120):
        current = page.url
        if ("login.microsoftonline.com" not in current
                and "login.windows.net" not in current
                and "devicelogin" not in current):
            break
        time.sleep(1)
    else:
        print("Timed out waiting for login.", file=sys.stderr)
        browser.close()
        edge_proc.terminate()
        sys.exit(1)

    # Give the SPA time to render
    print("Login complete — waiting for SPA to render...",
          file=sys.stderr, flush=True)
    try:
        page.wait_for_load_state("networkidle", timeout=30_000)
    except Exception:
        pass  # best-effort
    time.sleep(5)

    text = page.inner_text("body")
    # Don't close the user's Edge — just disconnect
    browser.close()

if len(text) > MAX_LENGTH:
    text = text[:MAX_LENGTH]

print(f"Fetched {len(text)} chars from S360.", file=sys.stderr, flush=True)

# --- Step 2: Send to LLM for summarization ---
config = LLMConfig(
    provider="azure_openai",
    model="gpt-5.2",
    base_url="https://open-ai-poc.openai.azure.com",
    deployment="gpt-5.2",
    api_version="2024-12-01-preview",
    timeout=120.0,
)
llm_auth = AzureChainedAuth()

prompt = (
    "Summarize this page comprehensively. "
    "Include the purpose of the tool, key features, "
    "who uses it, and any important concepts or metrics shown."
)
augmented = _build_context_prompt(URL, text, prompt)

with LLMClient(config, auth=llm_auth) as client:
    response = client.complete(augmented)
    print(response)
