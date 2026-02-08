# LLM Extender

A provider-agnostic Python library for calling LLMs through a unified interface, with synchronous and asynchronous support.

## Installation

```bash
pip install -e .
```

## Quick Start

```python
from llm_extender import LLMClient, LLMConfig

# Configure
config = LLMConfig(
    provider="openai",
    model="gpt-4",
    api_key="sk-...",  # Or use env var
)

# Synchronous usage
with LLMClient(config) as client:
    response = client.complete("What is the capital of France?")
    print(response)

# Asynchronous usage
async with LLMClient(config) as client:
    response = await client.acomplete("What is the capital of France?")
    print(response)
```

## Configuration

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `provider` | `str` | Yes | — | Provider name (e.g., `"openai"`) |
| `model` | `str` | Yes | — | Model identifier (e.g., `"gpt-4"`) |
| `api_key` | `str` | No | `""` | API key for authentication (or use auth strategies) |
| `base_url` | `str \| None` | No | `None` | Override provider endpoint |
| `timeout` | `float` | No | `30.0` | HTTP timeout in seconds |

### Custom Endpoint

Use `base_url` for compatible APIs (Together, Groq, LM Studio, etc.):

```python
config = LLMConfig(
    provider="openai",
    model="meta-llama/Llama-3-70b",
    api_key="...",
    base_url="https://api.together.xyz",
)
```

## Authentication Strategies

Instead of hardcoding `api_key`, use pluggable auth strategies that resolve credentials at runtime:

### Environment Variable

```python
from llm_extender import LLMClient, LLMConfig, EnvVarAuth

config = LLMConfig(provider="openai", model="gpt-4")
auth = EnvVarAuth("OPENAI_API_KEY")

with LLMClient(config, auth=auth) as client:
    response = client.complete("Hello")
```

### Custom Callback

```python
from llm_extender import LLMClient, LLMConfig, CallbackAuth

def get_key_from_vault() -> str:
    # Your key retrieval logic here
    return "sk-..."

config = LLMConfig(provider="openai", model="gpt-4")
auth = CallbackAuth(callback=get_key_from_vault)

with LLMClient(config, auth=auth) as client:
    response = client.complete("Hello")
```

### Azure Managed Identity

```python
from llm_extender import LLMClient, LLMConfig, ManagedIdentityAuth

# Requires: pip install azure-identity
config = LLMConfig(provider="openai", model="gpt-4", base_url="https://your-resource.openai.azure.com")
auth = ManagedIdentityAuth()

with LLMClient(config, auth=auth) as client:
    response = client.complete("Hello")
```

### Azure Chained Auth (CLI → MSI → API Key)

Automatic credential resolution with a predictable, explicit chain:

```python
from llm_extender import LLMClient, LLMConfig, AzureChainedAuth

# Requires: pip install azure-identity
config = LLMConfig(
    provider="azure_openai",
    model="gpt-4o",
    base_url="https://your-resource.openai.azure.com",
    deployment="gpt-4",
)

# Tries: Azure CLI → Managed Identity → fail
auth = AzureChainedAuth()

with LLMClient(config, auth=auth) as client:
    response = client.complete("Hello from Azure!")
```

The `scope` parameter can target different Azure AD resources:

```python
# For Azure Cognitive Services (default)
llm_auth = AzureChainedAuth()

# For Microsoft Graph or custom APIs
url_auth = AzureChainedAuth(scope="https://graph.microsoft.com/.default")
```

### Security

- Credentials are **never** persisted to disk or logged
- `repr()` and `str()` of auth objects never expose secret values
- `api_key` is excluded from `repr()` of `LLMConfig`

## Error Handling

All exceptions inherit from `LLMExtenderError`:

```python
from llm_extender import LLMExtenderError
from llm_extender.exceptions import (
    UnsupportedProviderError,
    ProviderError,
    AuthenticationError,
)

try:
    result = client.complete("Hello")
except AuthenticationError as e:
    print(f"Auth failed: {e}")     # Missing env var, bad callback, etc.
except ProviderError as e:
    print(f"Provider failed: {e}")  # HTTP errors, API errors
except UnsupportedProviderError as e:
    print(f"Unknown provider: {e}")
except LLMExtenderError as e:
    print(f"Library error: {e}")    # Catch-all
```

## Supported Providers

| Provider | Name | Notes |
|---|---|---|
| OpenAI | `"openai"` | Also works with any OpenAI-compatible API |
| Azure OpenAI | `"azure_openai"` | Uses deployment-based URLs with Azure AD token auth |

### Azure OpenAI

```python
from llm_extender import LLMClient, LLMConfig, AzureChainedAuth

config = LLMConfig(
    provider="azure_openai",
    model="gpt-4o",
    base_url="https://your-resource.openai.azure.com",
    deployment="your-deployment-name",
)

# Automatic: Azure CLI (local dev) → MSI (production) → API key (fallback)
auth = AzureChainedAuth()

with LLMClient(config, auth=auth) as client:
    response = client.complete("Hello from Azure!")
```

## URL Content Fetcher

Fetch web page content and inject it as LLM context — useful for summarizing articles, answering questions about online content, or grounding responses with real data.

```python
from llm_extender import LLMClient, LLMConfig, AzureChainedAuth

config = LLMConfig(
    provider="azure_openai",
    model="gpt-4o",
    base_url="https://your-resource.openai.azure.com",
    deployment="gpt-4",
)
auth = AzureChainedAuth()

with LLMClient(config, auth=auth) as client:
    # Fetch a URL and ask a question about it
    response = client.complete_with_url(
        prompt="List the key points from this page",
        url="https://example.com/article",
    )
    print(response)
```

### Authenticated URL Fetches

For URLs that require authentication (e.g., internal APIs, Azure-hosted content):

```python
from llm_extender import AzureChainedAuth

# LLM auth for the provider
llm_auth = AzureChainedAuth()

# Separate auth for the URL fetch (different scope)
url_auth = AzureChainedAuth(scope="https://graph.microsoft.com/.default")

with LLMClient(config, auth=llm_auth) as client:
    response = client.complete_with_url(
        prompt="Summarize this document",
        url="https://internal.example.com/doc",
        url_auth=url_auth,
    )
```

### Standalone Fetch

Use `fetch_url` / `afetch_url` directly without an LLM call:

```python
from llm_extender import fetch_url

text = fetch_url("https://example.com/page", max_length=10_000)
print(text)  # Plain text, HTML stripped
```

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v
```

## License

See [LICENSE](LICENSE) for details.
