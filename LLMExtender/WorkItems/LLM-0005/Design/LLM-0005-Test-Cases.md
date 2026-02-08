# LLM-0005 — Test Cases

## TC-1: Azure CLI credential succeeds (AC-2, step 1)
- Mock `AzureCliCredential.get_token()` to return a token
- Verify `resolve()` returns the CLI token
- Verify MSI is never called (CLI wins)

## TC-2: CLI fails, MSI succeeds (AC-2, step 2)
- Mock CLI to raise exception, MSI to return token
- Verify `resolve()` returns the MSI token

## TC-3: CLI fails, MSI fails, API key succeeds (AC-2, step 3)
- Mock both CLI and MSI to raise, provide `api_key="test-key"`
- Verify `resolve()` returns `"test-key"`

## TC-4: All three fail → AuthenticationError (AC-2, step 4)
- Mock CLI and MSI to raise, no API key
- Verify `AuthenticationError` is raised with all methods listed

## TC-5: Custom scope is passed to credentials (AC-3)
- Provide custom scope, mock CLI to succeed
- Verify `get_token()` is called with the custom scope

## TC-6: Default scope is cognitiveservices (AC-3)
- No scope arg, mock CLI to succeed
- Verify `get_token()` called with `https://cognitiveservices.azure.com/.default`

## TC-7: azure-identity not installed → falls to API key (AC-6)
- Patch `azure.identity` to None (ImportError)
- Provide `api_key="fallback"`
- Verify returns `"fallback"`

## TC-8: azure-identity not installed, no API key → fail (AC-6)
- Patch `azure.identity` to None
- No API key
- Verify `AuthenticationError`

## TC-9: async resolve — CLI succeeds (AC-5)
- Mock async `AzureCliCredential.get_token()` 
- Verify `aresolve()` returns CLI token

## TC-10: async resolve — full chain fallback (AC-5)
- Mock async CLI and MSI to fail, provide API key
- Verify `aresolve()` returns API key

## TC-11: repr does not leak credentials (security)
- Verify `repr()` shows class name with `***`

## TC-12: Subclass of AuthStrategy (AC-1)
- Verify `isinstance(AzureChainedAuth(...), AuthStrategy)`

## TC-13: Docstrings present
- Verify class and methods have docstrings
