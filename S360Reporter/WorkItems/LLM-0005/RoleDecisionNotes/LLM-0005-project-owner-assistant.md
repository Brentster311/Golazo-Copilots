# LLM-0005 — Project Owner Assistant Notes

## Decision: Single story, not decomposed
The request is a single auth strategy class — one user-observable outcome (new `AzureChainedAuth`). No decomposition needed.

## PO Direction: No DefaultAzureCredential
PO explicitly directed: "never use default credential, first try azure cli, then try MSI, then check for key, then fail." The chain is deliberate and explicit — Azure CLI → MSI → API key → error.

## Scope Justification
- Today: User must manually fetch tokens via `az account get-access-token` and wire up `CallbackAuth`.
- After: `AzureChainedAuth()` — one line, automatic credential resolution with a predictable, transparent chain.
- Differs from `DefaultAzureCredential` which tries ~8 credential types in an opaque order. This chain is 3 steps, fully visible.

## Must-Ask Checklist
- [x] Interface type: Python library (established)
- [x] Target platform: Cross-platform (established)
- [x] Data persistence: N/A (stateless token acquisition)
- [x] User type: Developers (established)

All items already established by prior work items.
