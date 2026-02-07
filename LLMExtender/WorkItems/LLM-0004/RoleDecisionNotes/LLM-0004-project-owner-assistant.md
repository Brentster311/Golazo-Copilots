# LLM-0004 — Project Owner Assistant Notes

## Date: 2026-02-07

## Summary
Captured user story for Azure OpenAI Provider based on PO's confirmed Azure setup.

## Key Decisions
- **Deployment target**: PO's `open-ai-poc` resource with `gpt-5.2` deployment (model version 2025-12-11)
- **Auth approach**: Azure AD only — local API keys are disabled on PO's resource
- **Provider name**: `azure_openai` in the provider registry
- **API key auth out of scope**: PO's resource has local auth disabled, so only Azure AD token auth is needed

## PO Confirmation
- PO confirmed all 7 acceptance criteria
- PO verified Azure resource is live (playground chat responded successfully)
