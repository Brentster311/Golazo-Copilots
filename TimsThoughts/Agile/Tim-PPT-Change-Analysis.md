# Tim's Proposed Changes: People, Process, and Technology
*With Gap Analysis Against the Synchronicity Requirement for Effective Change*

*Date: 2026-04-07 | Sources: SRC-005, SRC-007, SRC-008, SRC-009*

---

## Framework Note

Effective organizational change requires simultaneous movement across all three dimensions — **People, Process, and Technology** — in synchrony. Changing only one or two creates drag: new processes without the right people behaviors produce compliance theater; new technology without process change produces expensive shelf-ware; new people expectations without process or tooling support produce burnout and cynicism.

Tim's corpus is evaluated against this standard below.

---

## Part 1: What Tim Is Proposing

### People

| Change | Source |
|---|---|
| Senior leaders must wear two hats simultaneously: IC depth + leadership judgment | Senior IC Leader |
| Every mission team must have a single named accountable lead | Delivery Manifesto, Harambee |
| PMs redefined as clarity engines, not traffic controllers or backlog operators | Senior IC Leader, Infinite Game |
| Architects redefined as active reality shapers, not review boards | Senior IC Leader |
| Tech Leads redefined as execution owners, not consensus facilitators | Senior IC Leader |
| Engineering Managers redefined as execution multipliers, not people-only managers | Senior IC Leader |
| All leaders must maintain hands-on proximity to the work ("lean in") | Senior IC Leader |
| Cross-team direct contribution expected of engineers | Harambee, Delivery Manifesto |
| Earned headcount: growth tied to demonstrated throughput improvement | Delivery Is Existential |
| Performance addressed early, directly, never silently | Delivery Manifesto |
| Humans move up the value chain as AI absorbs mechanical work | AWARE (SRC-007) |
| AI adoption is not optional — it is a professional expectation | AWARE, Infinite Game |
| Escalation is reframed as leadership, not weakness | Delivery Manifesto |

---

### Process

| Change | Source |
|---|---|
| Weekly proof of progress: evidence gate (capability, reliability, risk retired, integration, gate cleared) | Delivery Manifesto |
| Single plan of record per mission team: commitments, dates, dependencies, named parties | Delivery Manifesto |
| Clean escalation protocol: blocker + impact + what was tried + decision needed + time sensitivity | Delivery Manifesto |
| Mission team structure: named lead + mission + scope + success metrics + interfaces + known dependencies | Harambee, Delivery Manifesto |
| Composition by default: design for interfaces; partner early; surface dependencies at design time, not integration | Harambee |
| Open repositories by default: merit-based contributions, clear maintainers | Delivery Manifesto, Harambee |
| Steel threads as durable, continuously exercised value streams replacing project-based delivery | Infinite Game |
| Product thinking as operating discipline: north stars, tradeoffs, health signals, not only backlogs | Infinite Game, Senior IC Leader |
| Program management as system integrator maintaining steel thread coherence at scale | Infinite Game |
| Quality, security, and compliance as continuous gates — not final-stage checks | Delivery Manifesto |
| Failed gates stop forward motion; issues addressed at source | Delivery Manifesto |
| Living artifacts in repos replace static documents in email and slide decks | Senior IC Leader, Delivery Manifesto |
| AI integrated across full PM-Dev-Quality-Ops lifecycle, not as an add-on | AWARE (SRC-007) |
| Specs structured around customer/business impact first, not documentation of past decisions | AWARE (SRC-007) |
| 100% test coverage treated as a feature, not a chore — AI generates, humans validate intent | AWARE (SRC-007) |
| Toil reduction as an explicit leadership accountability | Delivery Manifesto |
| Standards and reuse as default — not per-team invention | Delivery Manifesto |

---

### Technology

| Change | Source |
|---|---|
| AI embedded across the full lifecycle: spec, design, code, test, ops | AWARE (SRC-007), Infinite Game |
| AI generates: competing architectures, tradeoff tables, risk registers, test matrices | AWARE (SRC-007) |
| AI absorbs: boilerplate code, test scaffolding, spec drafting, documentation reformatting | AWARE (SRC-007) |
| Open repositories as the default infrastructure for cross-team contribution | Delivery Manifesto, Harambee |
| Steel threads as technical constructs: durable end-to-end value streams maintained in production | Infinite Game |
| Living artifacts maintained in version-controlled repos, not email or slide decks | Senior IC Leader |
| AI-augmented full lifecycle development: PM-Dev-Quality-Ops chain as an integrated system | Delivery Manifesto, AWARE |
| Systems that make "the right behavior the easy behavior" | Delivery Is Existential |

---

## Part 2: Gap Analysis Against the Synchronicity Requirement

### Gap 1 — Technology changes are called for, but the specific tooling is not specified

**What Tim says:** AI embedded everywhere; open repos; living artifacts in repos; AI generates tests and architectures.

**What is missing:** Tim does not specify *which* tools, *which* platforms, *which* AI systems, or *which* standards govern their use. He does not address:
- What counts as a compliant "open repo" (GitHub? Internal ADO? What branch policies?)
- What AI tools are approved, governed, and supported (guardrails are mentioned but not defined)
- What the artifact format is for a "living artifact" (markdown? wiki? structured template?)
- How evidence gates are captured and made visible (dashboard? ticket system? standup format?)

**Risk:** Teams will interpret "use AI" and "open repos" however is easiest locally, producing the exact fragmentation Tim is trying to eliminate.

---

### Gap 2 — People expectations change, but incentive and compensation systems are not addressed

**What Tim says:** Meritocracy of contribution; earned headcount; performance addressed early; "change what we incent and reward" (invitation email only — never specified in the five documents).

**What is missing:** Tim never describes *how* the incentive structure changes. He calls for new behaviors without addressing:
- How individual performance reviews will be updated to reflect the new expectations
- Whether promotion criteria change (currently, many orgs promote for visibility and influence, not delivery throughput)
- How the earned headcount model interacts with existing budgeting and HC approval processes
- Whether there are consequences for managers who don't hold the new bar — or only for the teams

**Risk:** People will observe that the formal rewards system still values the old behaviors and rationally continue performing them while nominally adopting the new language. Tim's archaeology section is full of examples of exactly this outcome.

---

### Gap 3 — Process changes assume organizational readiness that the People dimension doesn't establish

**What Tim says:** Weekly proof gates; single plan of record; clean escalation; living artifacts in repos.

**What is missing:** Many of these process changes require skills that are not taught or developed:
- Writing good specs that start with customer/business impact is a skill that "become a clarity engine" doesn't automatically confer
- Structured escalation (blocker + impact + tried + decision needed + sensitivity) requires practice and psychological safety — neither is addressed
- Maintaining living artifacts requires tooling fluency and discipline that varies widely across teams

**Risk:** The process is defined but the people capability to execute it is assumed rather than built. New processes imposed on underprepared people produce cargo-cult compliance.

---

### Gap 4 — AI adoption (Technology + Process) is prescribed, but worker resistance (People) is not addressed

**What Tim says:** AI is expected; humans move up the value chain; AI eliminates toil; embed AI in every step.

**What is missing:** Tim's AWARE document acknowledges the full adoption spectrum (enthusiasts, "next big thing" thinkers, cautious-confused, performative adopters) but does not address:
- How to help resistant or confused workers adopt without coercion
- What support systems exist for workers who feel their competence is threatened
- How to prevent the "algorithmic cage" dynamic where mandated AI use feels like loss of autonomy (directly described in HBR SRC-010)
- How to prevent shadow/unofficial AI use that bypasses standards

**Risk:** Mandate without support produces the BCG 31% sabotage statistic. The technology changes are announced; the psychological change management is absent. This is the exact gap SRC-010 (Hermann et al.) documents in detail.

---

### Gap 5 — The transition state is entirely unaddressed across all three dimensions

**What Tim says:** The target operating model is described in detail (mission teams, steel threads, weekly evidence, named leads, open repos, AI-embedded lifecycle).

**What is missing:** Tim does not describe how to get from the current state to the target state for *any* of the three dimensions:
- **People:** How do existing managers, PMs, and architects transition to the new role definitions? What support do they get? What happens to those who can't or won't?
- **Process:** How do teams mid-flight on current delivery commitments adopt mission team structures without disrupting existing obligations? What is the sequencing?
- **Technology:** What is the rollout plan for AI tooling? How do teams migrate from closed to open repos without breaking existing access controls and ownership patterns?

**Risk:** Without transition mechanics, the model is either adopted sporadically (the motivated few) or mandated abruptly (producing resistance across all three dimensions simultaneously). Both are common failure modes for transformation efforts.

---

### Gap 6 — Standards and reuse (Process/Technology) require governance that isn't specified

**What Tim says:** Standards and reuse are the default; open repos; meritocracy of contribution; anyone can fix issues where they occur.

**What is missing:** Open contribution and shared standards require a governance model:
- Who decides what a standard is? Who enforces it?
- When two teams disagree on a shared component's direction, who resolves it?
- What is the process for deprecating old standards when better ones emerge?
- How is meritocracy adjudicated when contributions are contested? (Meritocracy requires judges — Tim assumes the judgment is obvious.)

**Risk:** "Open by default" without governance produces a tragedy of the commons — shared components drift toward the needs of the loudest contributor rather than the system's conceptual integrity.

---

### Gap 7 — Technology changes free up human capacity, but there is no plan for what humans do with it

**What Tim says:** AI absorbs toil (mechanical code, test scaffolding, documentation drafting). Humans move up the value chain.

**What is missing:** "Moving up the value chain" is described as the destination but not the path:
- What does an engineer trained on execution-level work actually do when AI absorbs it?
- What training, coaching, or role scaffolding enables the transition from task executor to judgment holder?
- What happens in the intermediate period when AI is absorbing tasks but humans haven't yet developed the higher-order skills to fill the gap?

**Risk:** Technology displaces work before people have the skills to occupy the higher-value space. The result is not productivity gain — it is disorientation, underutilization, and the kind of competence threat the HBR article describes.

---

## Part 3: Synchronicity Summary

| Dimension | Tim's Coverage | Synchronicity Gap |
|---|---|---|
| **People** | Role redefinition, accountability expectations, AI adoption mandate | No incentive alignment, no transition support, no resistance management, no skills development path |
| **Process** | Highly detailed — weekly gates, single plan, escalation protocol, mission team structure, steel threads | Assumes people capability that hasn't been built; no transition sequencing; no governance for shared standards |
| **Technology** | Direction clear (AI embedded, open repos, living artifacts) | No specific tooling, platforms, or standards; no guardrails defined; no measurement infrastructure for evidence gates |

**The core synchronicity failure:** Tim's process specification is his most developed dimension. His technology direction is clear but underspecified. His people dimension — the hardest and slowest to change — receives the least concrete support: new expectations are announced, new roles are named, but the structural enablers (incentives, training, psychological safety, transition mechanics) are largely absent.

In classic change management terms: Tim has written the *what* and the *why* with precision. He has not written the *how* — and the *how* is almost entirely a people and transition problem.

---

## Implication for a Response to Tim

The most productive response acknowledges Tim's model is directionally correct and well-reasoned, then focuses precisely on the synchronicity gaps as implementation risks — not ideological objections. The frame is:

> *"The model is strong. The risk is in the transition. Here is what needs to be added to make the people and technology dimensions move with the process dimension — or the process changes will produce exactly the coordination theater you are trying to eliminate."*
