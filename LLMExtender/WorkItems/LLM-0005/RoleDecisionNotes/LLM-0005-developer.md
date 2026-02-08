# LLM-0005 — Developer Notes
- Tests written first (18 tests in test_auth_azure_chained.py)
- Implemented `AzureChainedAuth` in `llm_extender/auth/azure_chained.py`
- Chain: Azure CLI → MSI → API key → fail
- Configurable `scope` for LLM-0006 reuse
- Updated exports in `auth/__init__.py` and `__init__.py`
- Updated README with usage examples
- All 92 tests pass (74 existing + 18 new)
