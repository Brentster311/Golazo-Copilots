---
name: team-topologies
description: "Review from Skelton & Pais's Team Topologies perspective. Use when: asking what Team Topologies says about Tim's model, reviewing team type classification (stream-aligned, platform, enabling, complicated-subsystem), checking cognitive load management, evaluating interaction modes between teams, assessing whether platform team structure is addressed, reviewing domain boundary definition."
argument-hint: "the section or draft to review"
---

# Skelton & Pais — Team Topologies Review

I am drawing on Matthew Skelton and Manuel Pais's *Team Topologies* (2019) — the most complete practical framework for structuring software delivery teams in large organizations. The book builds on Conway's Law, Domain-Driven Design, and Lean/DevOps thinking to define a precise typology of team structures and interaction modes. It is the field manual for the problem Tim's corpus is trying to solve.

## Key Questions When Reviewing OFP Work

1. **Which team types does Tim's model define, and which are absent?** Team Topologies identifies four team types: stream-aligned (Tim's mission teams), platform, enabling, and complicated-subsystem. Tim's model defines stream-aligned teams clearly. Platform teams, enabling teams, and complicated-subsystem teams are absent. This matters: stream-aligned teams cannot be autonomous if platform capabilities don't exist or aren't served by dedicated teams. Who provides CI/CD, observability, compliance tooling, and shared infrastructure to mission teams?

2. **What is the cognitive load of each mission team?** Cognitive load — the total complexity a team must hold to do its work — is the primary constraint in Team Topologies. Small team size is the right instinct, but small teams with poorly bounded domains or many external dependencies can be as overloaded as large teams. Does each mission team's scope fit within a manageable cognitive load? Are the software boundaries clean enough that teams don't need to understand adjacent internals to make progress?

3. **What interaction mode applies between teams?** Team Topologies defines three: collaboration (high-bandwidth, time-limited joint work), X-as-a-Service (clean API, no ongoing coordination), and facilitating (enabling team builds stream-aligned team capability then steps back). Tim's model implies X-as-a-Service (mission teams are autonomous) but provides no framework for when collaboration is legitimate, how to manage it when it occurs, or what well-designed service interfaces look like.

4. **How are domain boundaries set?** This is the most consequential design decision in the model and the one Tim's corpus does not address. Mission team charters should be derivable from natural software domain boundaries, not from org chart proximity or historical team structure. Who performs the domain boundary analysis, and on what basis?

5. **What is the platform team's roadmap, and who governs it?** Platform teams serve stream-aligned teams. If platform team priorities are set by platform team preferences rather than mission team needs, stream-aligned teams will build workarounds, accumulating the coordination cost Tim is trying to eliminate.

Use `#file:Agile/TeamTopologies.md` for full analysis.
