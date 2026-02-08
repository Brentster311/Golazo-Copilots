# LLM-0008 Review Comments

## Architectural Notes
1. Keep `aad_browser.py` as a separate module — it has different concerns than the base auth strategies
2. JWT decoding should use `base64` only (no verification) — we just need the claims for UPN/tenant, not for security
3. MSAL is in-memory only — no persistent token cache
4. Device code flow prints to stderr (not stdout) so it doesn't interfere with piped output

## Risk
- Some AAD-protected sites won't work even with device code flow tokens (they need cookie-based auth from the redirect flow itself)
- Clear error messages for unsupported auth flows are critical
