# RETRO-002: Documentor Approved Unsupported Feature Claims

**Triggered during**: GCP-003 (README review)  
**Date**: 2026-01-20  
**Status**: RESOLVED

## Problem Observed
Documentor role approved README content that included an unsupported feature ("hotfix mode" in FAQ). The FAQ claimed Golazo supports expedited hotfix handling when the actual instructions have no such capability.

## Root Cause Analysis
1. Documentor role instructions focused on:
   - Artifact existence
   - Link validity  
   - Status updates
2. **Missing**: Validation that documentation claims are actually supported by implementation
3. No checkpoint requiring Documentor to verify claims against source of truth (`.github/copilot-instructions.md`)

## Proposed Process Change
Update Documentor role instructions to:
1. Add "Verify documentation accuracy" to Responsibilities
2. Add "Do not approve documentation that describes unsupported features" to Decision rules

## Impact Assessment
- Prevents publishing misleading documentation
- Adds ~1 minute to Documentor review
- Catches "aspirational" content before it confuses users

## Resolution
Updated `.github/roles/documentor.md`:
- Added to Responsibilities: "Verify documentation accuracy: Ensure all claims in user-facing docs (README, etc.) are actually supported by the implementation or instructions"
- Added to Decision rules: "Do not approve documentation that describes unsupported features — cross-reference README claims against `.github/copilot-instructions.md` and actual code"

Removed unsupported FAQ item from README.md.

## Lessons Learned
- Documentation is a form of contract with users — claims must be verifiable
- Documentor role needs to be a fact-checker, not just a formatter
- "Aspirational" features should not appear in documentation until implemented
