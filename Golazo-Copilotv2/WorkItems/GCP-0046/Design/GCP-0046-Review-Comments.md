# GCP-0046 Review Comments

## Design Review

### Overall Assessment
The design is clear, well-scoped, and follows existing patterns. The placement of `domain-expert` between PM and QA is sound — domain guidance feeds into the review rather than being a parallel afterthought.

### Issues Found

#### Issue 1: Backward Compatibility with In-Flight Work Items (Medium Risk)
The design doc mentions that "old state.json files referencing pre-domain-expert roles will still work" but doesn't detail the exact scenario. If a work item is currently at `program-manager` and the user transitions forward, the NEW `TRANSITIONS` dict will send them to `domain-expert` instead of `quality-assurance`. This is **correct and desired behavior**, but should be noted in release notes.

**Recommendation:** Add a note to the role's "First action" that if no Design Doc exists yet (i.e., the user skipped PM or PM didn't produce one), the domain-expert should still document "no design doc available, deferring domain analysis to QA phase."

#### Issue 2: Review Comments File May Not Exist Yet
The domain-expert role writes to `{id}-Review-Comments.md`, but this file is normally created by Quality Assurance. If domain-expert runs before QA, the file won't exist yet.

**Recommendation:** The domain-expert role should **create** the Review Comments file if it doesn't exist, using a standard header. QA then appends to it.

#### Issue 3: copilot-instructions.md Role Count
The copilot-instructions.md currently says "9 Roles" in various places. After this change it will be 10.

**Recommendation:** Update all references to role count in copilot-instructions.md.

### Positive Notes
- Using the existing Review Comments artifact avoids artifact proliferation
- Making the role mandatory (not skippable) is correct — even "no domain expertise needed" is a valid documented decision
- The trigger categories are comprehensive and well-organized
- The 3-copy deployment pattern is correctly identified

## Domain Expert Guidance
N/A — this work item modifies the Golazo Copilot workflow itself. No specialized domain expertise is required beyond understanding of the existing MCP server architecture.

## Architect Notes

### Architectural Alignment
The change is additive and aligns with the existing architecture:
- `transitions.py` is the single source of truth for role ordering — correctly scoped
- The role file pattern (3 copies: source default, deployed, package) is followed
- No new artifact types, no new MCP tools, no new data structures

### Contract Review
- The `role` parameter in `gcp_transition` accepts any string in `VALID_ROLES` — adding `"domain-expert"` to `TRANSITIONS` automatically adds it to `VALID_ROLES`. No API changes needed.
- `gcp_status` progress bar will automatically reflect 10 roles instead of 9.

### Security/Privacy
No concerns — role files are static markdown read by the MCP server at runtime. No user data, no credentials, no network calls.

### Scalability
N/A — adding one role to a 9-element list has zero performance impact.

### Approved
Design is architecturally sound. Proceed to implementation.
