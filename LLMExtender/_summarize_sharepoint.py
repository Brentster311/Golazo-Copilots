"""Summarize a SharePoint OneNote page via SharePoint REST API (no CDP, no device code).

Uses Azure CLI token with SharePoint scope to access the file directly,
then Graph API to get OneNote page content.
"""

import sys
import httpx

from llm_extender import AzureChainedAuth, LLMClient, LLMConfig
from llm_extender.url_fetcher import build_context_prompt, _html_to_text

URL = (
    "https://microsoft.sharepoint.com/teams/Azure_Compute_Insights/"
    "_layouts/15/Doc.aspx?sourcedoc={02b4c453-fe15-45bd-a125-f8eeb41a82b2}"
    "&action=edit&wd=target%28Eureka%20TSG%20Autopilot.one%7C018affa9-f7b5-"
    "4e90-bad6-b9033355dad5%2FWACAP%7C71f2a7fb-6ca0-454f-9e97-6cc8611c34cd"
    "%2F%29&wdorigin=NavigationUrl"
)

# The target page from the URL: section "Eureka TSG Autopilot", page "WACAP"
# Section group ID from URL: 018affa9-f7b5-4e90-bad6-b9033355dad5
# Page ID from URL: 71f2a7fb-6ca0-454f-9e97-6cc8611c34cd

SITE_HOST = "microsoft.sharepoint.com"
SITE_PATH = "/teams/Azure_Compute_Insights"

# --- Step 1: Try Graph API with the page ID from the URL ---
graph_auth = AzureChainedAuth(scope="https://graph.microsoft.com/.default")
token = graph_auth.resolve()
print(f"Graph token acquired ({len(token)} chars).", file=sys.stderr, flush=True)

graph_headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/json",
}

content = None

with httpx.Client(timeout=30.0, follow_redirects=True) as client:
    # Resolve site ID
    print("Resolving site...", file=sys.stderr, flush=True)
    site_resp = client.get(
        f"https://graph.microsoft.com/v1.0/sites/{SITE_HOST}:{SITE_PATH}",
        headers=graph_headers,
    )
    site_data = site_resp.json()
    site_id = site_data["id"]
    print(f"Site ID: {site_id}", file=sys.stderr, flush=True)

    # Try direct page content fetch using the page ID from the URL
    page_id = "71f2a7fb-6ca0-454f-9e97-6cc8611c34cd"
    print(f"Trying direct page fetch (id={page_id})...", file=sys.stderr, flush=True)

    # Try beta endpoint which may have broader permissions
    for api_ver in ["beta", "v1.0"]:
        page_resp = client.get(
            f"https://graph.microsoft.com/{api_ver}/sites/{site_id}/onenote/pages/{page_id}/content",
            headers=graph_headers,
        )
        print(f"  {api_ver}: {page_resp.status_code}", file=sys.stderr)
        if page_resp.status_code == 200:
            content = _html_to_text(page_resp.text)
            break

    # If Graph OneNote API doesn't work, try SharePoint REST API
    if content is None:
        print("\nGraph OneNote API failed. Trying SharePoint REST API...", file=sys.stderr, flush=True)

        sp_auth = AzureChainedAuth(scope="https://microsoft.sharepoint.com/.default")
        sp_token = sp_auth.resolve()
        sp_headers = {
            "Authorization": f"Bearer {sp_token}",
            "Accept": "application/json;odata=verbose",
        }

        # Get the file by its unique ID
        file_id = "02b4c453-fe15-45bd-a125-f8eeb41a82b2"
        sp_base = f"https://microsoft.sharepoint.com/teams/Azure_Compute_Insights"

        # Try getting file info
        file_resp = client.get(
            f"{sp_base}/_api/web/GetFileById('{file_id}')",
            headers=sp_headers,
        )
        print(f"  GetFileById: {file_resp.status_code}", file=sys.stderr)
        if file_resp.status_code == 200:
            file_data = file_resp.json()
            print(f"  File: {file_data.get('d', {}).get('Name', 'unknown')}", file=sys.stderr)

            # Try to get file content (binary .one file)
            content_resp = client.get(
                f"{sp_base}/_api/web/GetFileById('{file_id}')/$value",
                headers={
                    "Authorization": f"Bearer {sp_token}",
                },
            )
            print(f"  File content: {content_resp.status_code} ({len(content_resp.content)} bytes)", file=sys.stderr)

        # Try listing OneNote pages via SharePoint REST
        # Use the section/page IDs from the URL
        section_id = "018affa9-f7b5-4e90-bad6-b9033355dad5"
        print(f"\n  Trying OneNote REST endpoint...", file=sys.stderr, flush=True)

        on_resp = client.get(
            f"{sp_base}/_api/SP.Publishing.SitePageService/Pages",
            headers=sp_headers,
        )
        print(f"  SitePageService: {on_resp.status_code}", file=sys.stderr)

    # If still no content, try using the OneNote client URL pattern
    if content is None:
        print("\nTrying OneNote direct API with SharePoint token...", file=sys.stderr, flush=True)

        # OneNote pages can sometimes be accessed via the wopi endpoint
        on_token = sp_token  # reuse SharePoint token
        wopi_headers = {
            "Authorization": f"Bearer {on_token}",
            "Accept": "text/html",
        }

        # Try the OneNote Online rendering endpoint
        on_url = (
            f"https://ppc-onenote.officeapps.live.com/o/onenoteframe.aspx"
            f"?ui=en-US&rs=en-US&wopisrc=https%3A%2F%2Fmicrosoft.sharepoint.com"
            f"%2Fteams%2FAzure_Compute_Insights%2F_vti_bin%2Fwopi.ashx%2Ffolders"
            f"%2F02b4c453fe1545bda125f8eeb41a82b2"
        )
        on_resp = client.get(on_url, headers=wopi_headers)
        print(f"  OneNote frame: {on_resp.status_code} ({len(on_resp.text)} chars)", file=sys.stderr)
        if on_resp.status_code == 200 and len(on_resp.text) > 100:
            # Save raw HTML for inspection
            with open("_debug_onenote.html", "w", encoding="utf-8") as f:
                f.write(on_resp.text)
            print("  Saved raw HTML to _debug_onenote.html", file=sys.stderr)
            extracted = _html_to_text(on_resp.text)
            print(f"  Extracted text: {len(extracted)} chars", file=sys.stderr)
            if len(extracted.strip()) > 50:
                content = extracted

if content is None or len(content.strip()) < 50:
    print("\nAll API approaches returned insufficient content.", file=sys.stderr)
    print("SharePoint OneNote requires either:", file=sys.stderr)
    print("  1. Notes.Read.All permission in your token (not in Azure CLI default)", file=sys.stderr)
    print("  2. CDP browser approach (uses your real Edge session)", file=sys.stderr)
    sys.exit(1)

if len(content) > 50_000:
    content = content[:50_000]

print(f"\nExtracted {len(content)} chars.", file=sys.stderr, flush=True)

# --- Step 2: Summarize with LLM ---
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
    "Summarize this OneNote page comprehensively. "
    "Include the purpose, key topics discussed, important links, "
    "people involved, action items, and any technical details "
    "(clusters, databases, scenarios, etc.)."
)
augmented = build_context_prompt(URL, content, prompt)

with LLMClient(config, auth=llm_auth) as client:
    response = client.complete(augmented)
    print(response)
