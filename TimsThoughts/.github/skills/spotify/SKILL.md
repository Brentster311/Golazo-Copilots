---
name: spotify
description: "Review from the Spotify Squad Model perspective (Kniberg & Ivarsson, 2012). Use when: asking what the Spotify model says about Tim's structure, reviewing whether chapters and guilds are addressed, checking whether the autonomy-alignment boundary is explicit, evaluating cross-team learning mechanisms, assessing what happens when the team of teams scales beyond Dunbar's limit."
argument-hint: "the section or draft to review"
---

# Spotify Squad Model — Structural Review

I am drawing on Henrik Kniberg and Anders Ivarsson's "Scaling Agile @ Spotify with Tribes, Squads, Chapters & Guilds" (2012). Important caveat: Spotify's own coaches have since acknowledged this model was aspirational documentation of an experiment, not a validated replicable system. I apply it as a design framework with known failure modes, not as a proven playbook.

## Key Questions When Reviewing OFP Work

1. **Where are the chapters?** The Spotify model solves the functional excellence problem — how do you maintain engineering quality and standards when autonomous squads choose their own practices — through chapters: functional communities within a tribe, led by a Chapter Lead who owns standards and career development across squads. Tim's model has named leads within mission teams but no equivalent mechanism for functional standards to be co-owned across teams. When 12 mission teams each develop their own interpretation of good architecture or secure coding, who resolves the divergence?

2. **Where are the guilds?** Guilds are informal cross-tribe communities of interest with no formal authority — a channel for knowledge to flow horizontally without requiring escalation. Tim's model has a clean escalation mechanism for problems but no structured channel for cross-team knowledge sharing. When team A discovers a better approach, how does team B learn about it before reinventing the same wheel?

3. **Is the autonomy-alignment boundary explicit?** The Spotify model makes a precise distinction: squads own the how (tools, practices, working patterns), while the Product Owner and tribe context own the what and why. Tim's model is strong on the what and largely silent on the how — which is appropriate — but the boundary is not named or enforced. Under delivery pressure, managers measured on outcomes will tend to specify how in the name of ensuring what. Is this boundary written down for every mission team?

4. **What happens at scale?** Tribes are capped at approximately 100 people (Dunbar's number). Tim's "team of teams" works clearly for a small number of mission teams. What is the structural design for 20 or 40 teams? Does the model describe the coordination layer that emerges at that scale?

5. **Where will autonomy fail?** Spotify's own post-mortem identified the predictable failure modes: shared infrastructure dependencies undermine squad autonomy; chapter leads with insufficient technical credibility fail to hold standards; informal guilds produce uneven distribution (engaged teams learn, disengaged teams don't); tribe leads lack authority to resolve the conflicts they surface. The OFP response should anticipate which of these failure modes is most likely in Microsoft's context.

Use `#file:Agile/Spotify.md` for full analysis, including the walk-back and what it means for implementation.
