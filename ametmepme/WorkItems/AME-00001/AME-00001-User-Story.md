# AME-00001 — User Story

## Title
Explain the Differences Between AME, PME, TME, and CorpNet Tenants

## Goal
Produce a clear, well-referenced document that explains the purpose, security posture, access model, and intended use of each Microsoft tenant type: **AME**, **PME**, **TME**, and **CorpNet**.

## Background
Microsoft operates multiple Azure Active Directory (AAD) tenants with different security postures and intended workloads. Engineers working across Azure services need to understand:
- Which tenant to use for which type of work
- What access restrictions apply to each
- How identities and resources are isolated between tenants
- How the production lockdown affects their daily developer experience

## User Story
> As a **Microsoft engineer or developer**, I want to **understand the differences between AME, PME, TME, and CorpNet tenants** so that I can **correctly place resources, choose the right environment, and comply with production lockdown requirements**.

## Acceptance Criteria
- [ ] Document explains the purpose and intended use of each tenant (AME, PME, TME, CorpNet)
- [ ] Document covers security posture differences (SAW requirements, standing access, identity isolation)
- [ ] Document covers access restrictions (CorpNet access, cross-tenant consent, IP blocking)
- [ ] Document covers developer experience impact (tooling, credentials, eligibilities)
- [ ] Document includes references to source materials
- [ ] Document is in Markdown format and stored in this repository

## References
- [TME Overview](../../references/TME-Overview.md) — FAQ for Onboarding to the TME Tenant (source: SharePoint)

## Out of Scope
- Step-by-step onboarding instructions
- Tenant-specific resource provisioning guides
