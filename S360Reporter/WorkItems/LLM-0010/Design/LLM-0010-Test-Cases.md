# LLM-0010 — Test Cases

## TC-1: wait_for_aad_login returns when URL leaves AAD
- Mock page with URL on login.microsoftonline.com, then change to target URL
- Verify function returns without error

## TC-2: wait_for_aad_login raises on timeout
- Mock page that stays on login.microsoftonline.com
- Verify AuthenticationError raised after timeout

## TC-3: await_for_aad_login async variant works
- Same as TC-1 but async

## TC-4: Existing browser_auth="aad" tests still pass
- Run existing test suite
