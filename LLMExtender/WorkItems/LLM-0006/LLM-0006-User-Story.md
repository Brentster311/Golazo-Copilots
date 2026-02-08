# LLM-0006: URL Content Fetcher

## Status: BACKLOG

## User Story

- **Title:** URL Content Fetcher
- **As a:** developer using LLM Extender
- **I want:** to pass a URL to the client and have it fetch the page content, then include that content as context in my LLM prompt
- **So that:** I can ask questions about web pages, summarize articles, or analyze online content without manually downloading and pasting text

## Acceptance Criteria

1. New `fetch_url(url: str, auth: AuthStrategy | None = None) -> str` utility function that fetches a URL and extracts readable text content (strips HTML tags/scripts/styles). If `auth` is provided, the resolved token is sent as a `Bearer` header — enabling authenticated HTTPS fetches via `AzureChainedAuth` from LLM-0005.
2. New `complete_with_url(prompt: str, url: str, url_auth: AuthStrategy | None = None) -> str` method on `LLMClient` that fetches the URL content (optionally authenticated) and injects it as context before the user's prompt
3. Async variant `acomplete_with_url(prompt: str, url: str, url_auth: AuthStrategy | None = None) -> str` with the same behavior
4. Raises a clear error if the URL is unreachable or returns a non-success HTTP status (including 401/403 for auth failures)
5. Fetched content is truncated to a configurable max length to avoid exceeding token limits (default: 50,000 characters)
6. Uses the existing `httpx` dependency for HTTP requests (no new runtime dependencies for fetching)
7. `url_auth` is separate from the LLM auth — the LLM client's auth handles the LLM API call, while `url_auth` handles the URL fetch (they may use different scopes)

## Usage Example (target experience)

### Public URL (no auth needed for fetch)

```python
from llm_extender import LLMClient, LLMConfig
from llm_extender.auth import AzureChainedAuth

llm_auth = AzureChainedAuth()  # for the LLM API call
config = LLMConfig(
    provider="azure_openai",
    model="gpt-4o",
    base_url="https://open-ai-poc.openai.azure.com",
    deployment="gpt-4",
)

with LLMClient(config, auth=llm_auth) as client:
    answer = client.complete_with_url(
        prompt="Summarize this page in 3 bullet points",
        url="https://en.wikipedia.org/wiki/Olympia,_Washington",
    )
    print(answer)
```

### Authenticated URL (Azure AD-protected endpoint)

```python
# Separate auth for the URL fetch — different scope
url_auth = AzureChainedAuth(scope="https://graph.microsoft.com/.default")

with LLMClient(config, auth=llm_auth) as client:
    answer = client.complete_with_url(
        prompt="Summarize this internal document",
        url="https://internal.contoso.com/api/docs/123",
        url_auth=url_auth,  # token sent as Bearer header for the fetch
    )
    print(answer)
```

## Out of Scope

- JavaScript rendering (SPA pages) — only static HTML content
- PDF, image, or binary file parsing
- Recursive crawling / following links
- Persistent caching of fetched content

## Assumptions

- **Assumption (explicit):** HTML-to-text extraction uses a lightweight approach (regex or built-in `html.parser`) rather than adding `beautifulsoup4` as a dependency. If richer extraction is needed it can be a follow-up.
- **Assumption (explicit):** The prompt template wraps fetched content as: `"Content from {url}:\n\n{content}\n\n{user_prompt}"`. This is a sensible default; custom templates can be a future enhancement.

## Non-functional Requirements

- URL fetching must respect the configured `timeout` from `LLMConfig`
- No credentials or fetched content stored beyond the request lifecycle
- User-Agent header set to identify the library (e.g., `LLMExtender/1.0`)

## Telemetry / Metrics Expected

- N/A (library code, no telemetry)

## Rollout / Rollback Notes

- Additive change — new methods on `LLMClient`, no breaking changes to existing API
