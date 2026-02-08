# LLM-0008 Test Cases

## TC-1: MSI auth rejected
- Input: `browser_auth="aad"` with `ManagedIdentityAuth`
- Expected: `AuthenticationError` with message about user credentials required

## TC-2: MSI auth rejected (async)
- Same as TC-1 but async variant

## TC-3: browser_auth=None is default
- Input: inspect signature of `fetch_url`
- Expected: `browser_auth` parameter defaults to `None`

## TC-4: browser_auth passes through client
- Input: `complete_with_url(render_js=True, browser_auth="aad")`
- Expected: `fetch_url` called with `browser_auth="aad"`

## TC-5: browser_auth passes through client (async)
- Same as TC-4 but async

## TC-6: is_user_credential returns True for non-MSI
- Input: `EnvVarAuth`, `CallbackAuth`, `AzureChainedAuth`
- Expected: `True`

## TC-7: is_user_credential returns False for MSI
- Input: `ManagedIdentityAuth`
- Expected: `False`

## TC-8: decode_jwt_claims extracts upn and tid
- Input: a base64-encoded JWT with known claims
- Expected: returns dict with `upn` and `tid`

## TC-9: detect_aad_redirect
- Input: various URLs
- Expected: `True` for login.microsoftonline.com, `False` otherwise

## TC-10: parse_aad_authorize_url extracts params
- Input: AAD authorize URL with client_id, scope, etc.
- Expected: dict with extracted params

## TC-11: device code flow initiated with correct scope
- Input: mock MSAL PublicClientApplication
- Expected: `initiate_device_flow` called with correct scope

## TC-12: device code instructions printed to stderr
- Input: mock device code flow
- Expected: device code message printed to stderr

## TC-13: browser_auth requires render_js=True
- Input: `browser_auth="aad"` with `render_js=False`
- Expected: `ProviderError` explaining that browser_auth requires render_js=True

## TC-14: invalid browser_auth value rejected
- Input: `browser_auth="invalid"`
- Expected: `ProviderError` with valid options

## TC-15: Non-MSI auth allowed (EnvVarAuth)
- Input: `browser_auth="aad"` with `EnvVarAuth`
- Expected: no AuthenticationError (proceeds to browser flow)

## TC-16: Docstrings mention browser_auth
- Input: inspect docstrings
- Expected: `browser_auth` documented in fetch_url and afetch_url
