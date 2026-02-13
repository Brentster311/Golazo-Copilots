# Project Owner Assistant Decision Notes — EES-00006

## Scope Justification
Single user-observable outcome: a Settings dialog that persists Azure OpenAI configuration. Does not touch CLI behavior or authentication — additive only.

## Key Decisions
- **Config over env vars**: GUI settings override env vars, with fallback. This lets env-var users continue unchanged.
- **YAML config file**: Consistent with existing persistence pattern (ontology.yaml, rootcauses.yaml).
- **File menu placement**: Follows standard desktop app convention (File → Settings).
- **Defaults**: endpoint=`https://open-ai-poc.openai.azure.com/`, deployment=`gpt5.2`, api_version=`2025-12-11`.
