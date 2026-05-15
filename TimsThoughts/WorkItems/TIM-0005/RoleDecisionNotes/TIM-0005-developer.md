# TIM-0005 — Developer Decision Notes

## Implementation

Created 12 `.agent.md` files in `.github/agents/`. Each agent was authored fresh in first-person voice, drawing on the corresponding `Agile/*.md` source file. No third-person ("he would say") language.

## Files Created

| File | Author | Words (approx) |
|------|--------|----------------|
| al-shalloway.agent.md | Al Shalloway | ~350 |
| christopher-alexander.agent.md | Christopher Alexander | ~370 |
| daniel-pink.agent.md | Daniel Pink | ~380 |
| donald-reinertsen.agent.md | Donald Reinertsen | ~360 |
| eric-ries.agent.md | Eric Ries | ~340 |
| joseph-grenny.agent.md | Joseph Grenny | ~390 |
| kent-beck.agent.md | Kent Beck | ~360 |
| dean-leffingwell.agent.md | Dean Leffingwell | ~380 |
| mary-poppendieck.agent.md | Mary Poppendieck | ~370 |
| simon-sinek.agent.md | Simon Sinek | ~400 |
| starfish-spider.agent.md | Brafman & Beckstrom | ~390 |
| stephen-covey.agent.md | Stephen Covey | ~400 |

## YAML Frontmatter Pattern (applied to all 12)

```yaml
---
name: "Human-readable author name"
description: "Review from [Author]'s [framework] perspective. Use when: asking what [Author] would say, [trigger phrases]."
tools: [read, search]
user-invocable: true
---
```

All `description` values are quoted (colon safety). `name` field uses real author names. `tools: [read, search]` is minimal and read-only as specified.

## Tests Verified (Pre-Commit)

- [x] TC-01: `.github/agents/` directory exists
- [x] TC-02: Exactly 12 `.agent.md` files present
- [x] TC-03: All 12 expected filenames present
- [x] TC-04: All files open with `---` (YAML frontmatter)
- [x] TC-05: All files have human-readable `name:` field
- [x] TC-06: All descriptions are quoted, contain author name + trigger phrases
- [x] TC-07: All files specify `tools: [read, search]`
- [x] TC-08: All bodies use first-person author voice
- [x] TC-09: All bodies contain ≥ 4 distinct questions/concerns
- [x] TC-10: No invented positions — all concerns trace to Agile/*.md sources
- [x] TC-11: `user-invocable: true` explicit in all 12
- [ ] TC-12: Git commit — pending (builder role)
