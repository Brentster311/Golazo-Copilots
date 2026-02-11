# GCP-0041: Spine — Mention Capability Registry in bootstrap-instructions.md

**Status**: IMPLEMENTED

---

## User Story

- **Title**: Spine — Mention Capability Registry
- **As a**: GCP user reading the copilot-instructions.md (spine)
- **I want**: the spine to mention `gcp_capabilities` as an available tool and briefly describe when to use it
- **So that**: the LLM assistant knows the tool exists and can proactively use it even outside specific role instructions
- **Out of scope**:
  - Role instruction changes (GCP-0039)
  - Bootstrap scaffolding (GCP-0040)
  - Status hints (GCP-0042)
  - Detailed usage docs (the tool's own description suffices)
- **Assumptions**:
  - **Assumption (explicit)**: The spine is `bootstrap-instructions.md` (source) deployed as `.github/copilot-instructions.md` — inherited
  - **Assumption (explicit)**: Users are technical developers — inherited
- **Acceptance Criteria**:
  - AC1: `bootstrap-instructions.md` includes a section or mention of `gcp_capabilities` describing its purpose (impact analysis from capabilities.yaml)
  - AC2: The mention is conditional: "If a `capabilities.yaml` exists in the project root..."
  - AC3: The spine does NOT duplicate the full tool documentation — just a brief pointer
  - AC4: After `gcp_bootstrap`, the deployed `.github/copilot-instructions.md` contains the mention
- **Non-functional requirements**: Brevity — 3-5 lines maximum in the spine
- **Telemetry / metrics expected**: N/A
- **Rollout / rollback notes**: Next bootstrap propagates the updated spine
