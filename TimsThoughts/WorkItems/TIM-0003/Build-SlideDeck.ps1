# TIM-0003: Build Tim's Delivery Vision Slide Deck
# Output: Tims-Delivery-Vision.pptx (~33 slides, ~30 minutes)

$outputPath = "q:\src\Golazo-Copilots\TimsThoughts\WorkItems\TIM-0003\Tims-Delivery-Vision.pptx"

# Layout constants (PowerPoint ppLayout enum)
$ppLayoutTitle     = 1   # Centered title + subtitle  (section dividers, title slide)
$ppLayoutContent   = 2   # Title + content body (most slides)
$ppSaveAsPPTX      = 24  # ppSaveAsOpenXMLPresentation

$CR = [char]13  # Paragraph break in PPT text ranges

Write-Host "Starting PowerPoint..."
$pptApp = New-Object -ComObject PowerPoint.Application
$pptApp.Visible = 1  # must be visible to avoid COM errors
$deck = $pptApp.Presentations.Add(1)

# ------------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------------
function New-Slide($layout) {
    return $deck.Slides.Add($deck.Slides.Count + 1, $layout)
}

function slide-title-sub($titleText, $subText) {
    $s = New-Slide $ppLayoutTitle
    $s.Shapes.Item(1).TextFrame.TextRange.Text = $titleText
    $s.Shapes.Item(2).TextFrame.TextRange.Text = $subText
    return $s
}

function slide-content($titleText, [string[]]$bullets) {
    $s = New-Slide $ppLayoutContent
    $s.Shapes.Item(1).TextFrame.TextRange.Text = $titleText
    $body = $s.Shapes.Item(2).TextFrame.TextRange
    $body.Text = ($bullets -join "$CR")
    return $s
}

# ------------------------------------------------------------------
# SLIDE 1: Title
# ------------------------------------------------------------------
slide-title-sub `
    "Understanding Tim's Delivery Vision" `
    "A Review of the Five-Document Corpus | April 2026" | Out-Null

# ------------------------------------------------------------------
# SLIDE 2: Corpus Abstract
# ------------------------------------------------------------------
slide-content "The Big Idea: Five Documents, One Argument" @(
    "Across five documents, Tim argues that delivery capability is now existential — not optional, not incremental."
    "Organizations that cannot deliver continuously, safely, and at scale will lose: to AI-native competitors, to regulatory risk, and to customer defection."
    ""
    "The corpus builds a coherent, layered operating model:"
    "   Small accountable mission teams — not large diffuse organizations"
    "   Infinite-game mindset — steel threads, product thinking, no finish line"
    "   Synchronized cross-functional effort — Harambee: all pull together"
    "   Senior leaders who create clarity and maintain execution proximity"
    ""
    "This is both a diagnosis of why we are failing and a prescription for how to operate differently."
) | Out-Null

# ------------------------------------------------------------------
# SLIDE 3: Document Map
# ------------------------------------------------------------------
slide-content "How the Five Documents Connect" @(
    "The five documents form a progression from urgency to full operating model:"
    ""
    "1.  Delivery is Existential          WHY delivery matters now  (the urgency case)"
    "2.  The Delivery Manifesto           HOW we will operate       (the operating contract)"
    "3.  Delivery as an Infinite Game     WHAT game we are playing  (the mindset shift)"
    "4.  Harambee and Mission Teams       WHO executes and how      (the team model)"
    "5.  Role of the Senior IC Leader     WHO leads and how         (the leadership model)"
    ""
    "Read together, they describe a complete system — not a collection of independent ideas."
) | Out-Null

# ------------------------------------------------------------------
# SLIDE 4: Problem/Solution Overview
# ------------------------------------------------------------------
slide-content "Five Documents at a Glance: Problem  ->  Solution" @(
    "Delivery is Existential"
    "   Problem: Slow delivery = existential risk; activity rewarded over outcomes"
    "   Solution: Small teams, earned headcount, outcome metrics"
    ""
    "The Delivery Manifesto"
    "   Problem: Accountability diffusion; no single plan; quality gated out at the end"
    "   Solution: Named leads, one plan of record, weekly proof gates"
    ""
    "Delivery as Infinite Game"
    "   Problem: Finite mechanics applied to infinite systems — cloud, AI, compliance"
    "   Solution: Steel threads, product thinking, durable team charters"
    ""
    "Harambee and Mission Teams"
    "   Problem: Local optimization destroys systemic velocity; late dependency discovery"
    "   Solution: Explicit mission/scope/metrics per team; composition by default"
    ""
    "Senior IC Leader"
    "   Problem: Leaders too abstract or too local; clarity never produced"
    "   Solution: Two-hat leadership — IC depth + leader judgment; hands-on proximity"
) | Out-Null

# ==================================================================
# DOCUMENT 1: DELIVERY IS EXISTENTIAL
# ==================================================================

# SLIDE 5: Section Divider
slide-title-sub `
    "Delivery is Existential" `
    "The Urgency Case — Why Delivery Is No Longer Optional" | Out-Null

# SLIDE 6: What Tim Wants
slide-content "Delivery is Existential: What Tim Wants" @(
    "Startup-like execution culture inside the enterprise — urgency and ownership, not bureaucracy"
    "Outcomes and velocity prioritized over effort signals, status reporting, and activity"
    "Small, accountable teams with earned headcount — growth tied to demonstrated throughput improvement"
    "AI adoption as a productivity multiplier embedded across the full PM-Dev-Quality-Ops chain"
    "Business and platform results as the unit of success — not headcount, not meetings, not reports"
    "Leadership that changes how we operate, what we measure, and what we incent and reward"
) | Out-Null

# SLIDE 7: Why He Wants It
slide-content "Delivery is Existential: Why He Wants It" @(
    "AI disruption is changing the competitive landscape — organizations that deliver slower lose permanently"
    "Regulatory and sovereign cloud shifts (EU, SFI/QEI, Middle East) add compliance urgency on top of delivery urgency"
    "Large diffuse teams hide accountability gaps — no one is responsible when everyone is responsible"
    "The organization systemically rewards activity signals (reports, reviews, meetings), not material outcomes"
    "Headcount grows as the default response to delivery problems — this makes problems worse, not better"
    "Survival in the AI era requires the ability to deliver continuously, safely, and at hyperscale"
) | Out-Null

# SLIDE 8: Observed Gaps
slide-content "Delivery is Existential: Observed Gaps" @(
    "Teams report activity — meetings held, reviews conducted, slides produced — rather than shipping outcomes"
    "Accountability diffuses across large teams; no single person owns the result when it fails"
    "Headcount grows without corresponding improvement in throughput or quality"
    "AI tools are available but are not embedded systematically in the delivery and quality workflow"
    "Planning cycles generate artifact decks instead of working, deployed, and measured software"
    "Delivery is treated as a trailing indicator reviewed quarterly, not a real-time survival variable"
) | Out-Null

# SLIDE 9: Proposed Solution
slide-content "Delivery is Existential: Proposed Solution" @(
    "Small focused teams accountable for clearly bounded missions — conceptual integrity at team level"
    "Earned headcount: growth tied to demonstrated throughput and quality improvement, not org requests"
    "Replace effort metrics with outcome and velocity metrics — ship it, measure it, improve it"
    "Embed AI across PM-Dev-Quality-Ops to remove toil and continuously raise the quality bar"
    "Treat delivery speed as a competitive survival variable — not a lagging indicator"
    "Fundamentally change what we operate, what we measure, and what we incent and reward"
) | Out-Null

# ==================================================================
# DOCUMENT 2: THE DELIVERY MANIFESTO
# ==================================================================

# SLIDE 10: Section Divider
slide-title-sub `
    "The Delivery Manifesto" `
    "The Operating Contract — How We Will Work" | Out-Null

# SLIDE 11: What Tim Wants
slide-content "The Delivery Manifesto: What Tim Wants" @(
    "Explicit accountability: named accountable lead per mission team — not 'the team' owns it"
    "Meritocracy of contribution: what you deliver matters, not your role, tenure, or title"
    "Open repositories and cross-team direct contribution — not escalation — as the default mechanism"
    "Weekly proof of progress: capability delivered, reliability improved, risk retired, integration completed"
    "Single plan of record: one visible execution plan per team with commitments, dates, dependencies, named leads"
    "Clean escalation as a leadership discipline — silence is failure; escalation is leadership"
) | Out-Null

# SLIDE 12: Why He Wants It
slide-content "The Delivery Manifesto: Why He Wants It" @(
    "Scale creates entropy — without explicit operating contracts, accountability diffuses into the organization"
    "Multiple competing plans = nobody is accountable for the actual plan that matters"
    "Silent blockers kill more deliveries than technical problems — escalation is not weakness"
    "'Ownership' language without explicit accountability is performance theater — it changes nothing"
    "Large organizations systemically reward plan-generation over plan-execution — the manifesto counters this"
    "Quality, security, and compliance pushed to the end as gates are how technical debt becomes existential debt"
) | Out-Null

# SLIDE 13: Observed Gaps
slide-content "The Delivery Manifesto: Observed Gaps" @(
    "Teams maintain multiple informal plans — no single source of truth; plans serve different audiences"
    "Blockers go unreported until they become crises — safety-motivated silence treated as professionalism"
    "'Ownership' claimed without real scope authority or decision rights to back it up"
    "Quality and compliance treated as final delivery gates, not continuous disciplines woven into execution"
    "AI not yet embedded as standard practice — used as an experiment or optional add-on"
    "Narrative without material evidence accepted as 'progress' in reviews and check-ins"
) | Out-Null

# SLIDE 14: Proposed Solution
slide-content "The Delivery Manifesto: Proposed Solution" @(
    "Nine-principle operating contract: accountability, mission teams, composition, meritocracy, toil reduction,"
    "   standards/reuse, AI productivity, living artifacts, execution rhythms"
    "Weekly proof gates: evidence required — capability | reliability | risk retired | integration | gate cleared"
    "One plan of record: commitments, dates, dependencies, named accountable parties — visible to all"
    "Clean escalation protocol: state the blocker + impact + what was tried + decision needed + time sensitivity"
    "Failed quality gates stop forward motion — issues addressed at the source, never pushed downstream"
    "Silence is failure. Escalation is leadership."
) | Out-Null

# ==================================================================
# DOCUMENT 3: DELIVERY AS AN INFINITE GAME
# ==================================================================

# SLIDE 15: Section Divider
slide-title-sub `
    "Delivery as an Infinite Game" `
    "The Mindset Shift — What Kind of Game Are We Actually Playing?" | Out-Null

# SLIDE 16: What Tim Wants
slide-content "Delivery as Infinite Game: What Tim Wants" @(
    "Infinite-game orientation: no finish line, continuous improvement — 'done' is not a destination"
    "Just Cause: be the most reliable, enterprise-grade, AI-ready hyperscale cloud — now and always"
    "Steel threads: durable, continuously exercised value streams that run end-to-end across domains"
    "Product thinking as an operating discipline — not a role, not a phase, not a handoff"
    "PM as force multiplier and clarity engine — not a backlog operator"
    "Program management as integrator — maintaining coherence across steel threads as the org scales"
) | Out-Null

# SLIDE 17: Why He Wants It
slide-content "Delivery as Infinite Game: Why He Wants It" @(
    "Digital/AI platforms do not stabilize after delivery — they live in production permanently"
    "Regulations shift, capacity needs evolve, threat models change — the environment never stops moving"
    "Finite mechanics (projects, temp teams, fixed scope) create organizational fragility in infinite systems"
    "Finite-game thinking means winning locally while losing systemically — the death move for a platform org"
    "Trust is an engineering input: without it, teams hoard work, avoid surfacing risk, create brittle systems"
    "Models drift. Interfaces evolve. Threats adapt. Projects end. Products — and steel threads — endure."
) | Out-Null

# SLIDE 18: Observed Gaps
slide-content "Delivery as Infinite Game: Observed Gaps" @(
    "Delivery managed as a series of projects — each one resets context, teams, and accountability"
    "Product management treated as a backlog operator or traffic controller, not a strategic clarity engine"
    "Compliance and quality declared 'done' at milestones rather than demonstrated continuously"
    "No language of steel threads or durable ownership — every execution cycle starts over"
    "PM and program management roles treated as coordination overhead, not strategic organizational inputs"
    "Success defined as 'shipped it once' — not 'the system is healthier than last quarter'"
) | Out-Null

# SLIDE 19: Proposed Solution
slide-content "Delivery as Infinite Game: Proposed Solution" @(
    "Shift from project to product thinking: steel threads replace project milestones as the primary unit"
    "Primary steel thread = the service (continuous, durable, unambiguous)"
    "Supporting steel threads = engineering systems, compliance posture, change mgmt, capacity lifecycle"
    "Product thinking creates north stars, explicit tradeoffs, and health signals — not just backlogs"
    "Program management as integrator: coherence across steel threads as the organization scales"
    "Each execution cycle is finite. The game is infinite. Design and operate accordingly."
) | Out-Null

# ==================================================================
# DOCUMENT 4: HARAMBEE AND MISSION TEAMS
# ==================================================================

# SLIDE 20: Section Divider
slide-title-sub `
    "Harambee and Mission Teams" `
    "The Team Model — Who Executes and How" | Out-Null

# SLIDE 21: What Tim Wants
slide-content "Harambee and Mission Teams: What Tim Wants" @(
    "Harambee: 'all pull together' — synchronized force toward a shared goal, not informal alignment"
    "Every mission team has: named accountable lead | articulated mission and scope | explicit success metrics"
    "   | defined interfaces to other teams | known dependencies and integration points"
    "Dependencies surfaced early and managed deliberately — not discovered at integration"
    "Direct cross-team contribution as the default — not escalation as the first move"
    "Open repos with merit-based contributions and clear maintainers — scale quality and velocity simultaneously"
) | Out-Null

# SLIDE 22: Why He Wants It
slide-content "Harambee and Mission Teams: Why He Wants It" @(
    "Interconnected systems are destroyed by local optimization — your team's win becomes my team's blocker"
    "Informal alignment is not enough at scale — it creates coordination surprises at the worst moments"
    "Late dependency discovery is the most common avoidable cause of delivery delays"
    "Escalation as the default cross-team mechanism is too slow and creates organizational bottlenecks"
    "Accountability for outcomes requires visible scope, explicit success criteria, and a named human"
    "The fastest path to delivery is often direct contribution — not a meeting, not a ticket, not an escalation"
) | Out-Null

# SLIDE 23: Observed Gaps
slide-content "Harambee and Mission Teams: Observed Gaps" @(
    "Teams optimize for their own velocity while creating systemic drag for adjacent and dependent teams"
    "Dependencies discovered at integration time rather than at design and planning time"
    "Escalation used as the default cross-team mechanism — slow, bottlenecked, and accountability-destroying"
    "No consistent standard for what 'a mission team' means: scope, accountability, and interfaces vary widely"
    "Repos closed by default; contribution requires relationships rather than quality standards"
    "Composition treated as an optional design choice rather than the default execution expectation"
) | Out-Null

# SLIDE 24: Proposed Solution
slide-content "Harambee and Mission Teams: Proposed Solution" @(
    "Harambee model: every member pulls toward the shared mission — not just their individual component"
    "Every mission team defined with: named lead | mission + scope | success metrics | interfaces | dependencies"
    "Composition is the default: design for composition, partner early, expose clear interfaces"
    "Open repos enable the fastest delivery path — direct contribution, not escalation, to unblock"
    "Cross-team contribution encouraged: fix issues where they occur; improve shared components directly"
    "Accountability is explicit. Execution is collaborative."
) | Out-Null

# ==================================================================
# DOCUMENT 5: THE ROLE OF THE SENIOR IC LEADER
# ==================================================================

# SLIDE 25: Section Divider
slide-title-sub `
    "The Role of the Senior IC Leader" `
    "The Leadership Model — Who Leads and How" | Out-Null

# SLIDE 26: What Tim Wants
slide-content "Senior IC Leader: What Tim Wants" @(
    "Leaders wearing two hats simultaneously: IC depth (credibility, grounding) + leadership judgment (alignment)"
    "Clarity as the primary output of every senior leader — ambiguity is a leadership failure"
    "Hands-on leadership: lean in to standups, specs, designs, execution — no 'management by proxy'"
    "No reviews for reviews — context is inherent in how you work, not a stage-gate presentation"
    "PM = clarity engine (not traffic controller)"
    "Architect = coherence guardian (not review board)"
    "Tech Lead = execution owner (not consensus facilitator)"
    "EM = execution multiplier (not people-only manager)"
) | Out-Null

# SLIDE 27: Why He Wants It
slide-content "Senior IC Leader: Why He Wants It" @(
    "Distance creates drift; drift destroys velocity — the gap between leader and work is measured in failures"
    "IC-only leaders optimize locally and lose the system — deep but blind to cross-cutting failure modes"
    "Manager-only leaders perform 'coordination theater' — activity signals without delivery outcomes"
    "Leadership without IC grounding creates noise — direction without credibility"
    "IC work without leadership creates fragmentation — execution without system-level coherence"
    "Velocity is constrained by ambiguity, not effort — and ambiguity is a leadership product"
) | Out-Null

# SLIDE 28: Observed Gaps
slide-content "Senior IC Leader: Observed Gaps" @(
    "Leaders default to abstraction and review cycles rather than execution proximity"
    "PMs operating as backlog operators or traffic controllers — not writing durable clarity artifacts"
    "Architects operating as review boards with opinions — not active reality shapers making decisions"
    "EMs managing people metrics disconnected from actual execution constraints and technical reality"
    "Ambiguity persists through entire delivery cycles because the senior leader who should collapse it didn't"
    "Reviews created for the sake of reviews — consuming time without producing clarity or decisions"
) | Out-Null

# SLIDE 29: Proposed Solution
slide-content "Senior IC Leader: Proposed Solution" @(
    "Both hats required, always: IC ensures technical depth and credibility; leadership ensures alignment"
    "PM owns intent, outcomes, tradeoffs — written in durable living artifacts in repos, not email or pptx"
    "PM forces explicit scope, quality, and schedule tradeoffs — and documents the decisions"
    "Architect defines steel threads, invariants, domain boundaries — engaged early and continuously"
    "Tech Lead ships in thin testable increments, surfaces risk early, holds quality bar without heroics"
    "EM stays close enough to understand real constraints, develops talent without sacrificing momentum"
    "All leaders: lean in. Distance is not professionalism — it is decay."
) | Out-Null

# ==================================================================
# SYNTHESIZING SLIDES
# ==================================================================

# SLIDE 30: Recurring Themes
slide-content "Five Documents, Five Consistent Signals" @(
    "1.  Accountability must be explicit and named — not inferred, not collective, not optional"
    ""
    "2.  Small teams with clear scope outperform large diffuse teams — consistently and structurally"
    ""
    "3.  Material evidence replaces activity narrative — weekly, visible, no exceptions"
    ""
    "4.  AI is a productivity multiplier — not adopting it is falling behind by choice, not circumstance"
    ""
    "5.  Leaders create clarity and maintain execution proximity — or they fail the team"
    ""
    "Every document addresses all five signals from a different angle."
) | Out-Null

# SLIDE 31: Accountability Architecture
slide-content "How the Model Layers: The Accountability Architecture" @(
    "Layer 1 — Individual"
    "   Two-hat senior IC leader: IC depth + leadership judgment + hands-on execution proximity"
    ""
    "Layer 2 — Team"
    "   Mission team: named lead + explicit scope + success metrics + defined interfaces + known dependencies"
    ""
    "Layer 3 — Cross-Team"
    "   Harambee: composition by default, direct contribution over escalation, open repos"
    ""
    "Layer 4 — System"
    "   Steel threads + product thinking + infinite-game orientation (no 'done')"
    ""
    "Layer 5 — Culture"
    "   Meritocracy of contribution + living artifacts + weekly evidence + AI as standard practice"
) | Out-Null

# SLIDE 32: What This Means by Role
slide-content "What This Means for You: By Role" @(
    "PMs: You are clarity engines. Write intent, outcomes, and tradeoffs in repos — not email, not pptx."
    ""
    "Architects: You are active reality shapers. Engage early. Define steel threads. Hold invariants."
    ""
    "Tech Leads: You own execution and quality decisions. Surface risk — don't absorb it silently."
    ""
    "Engineering Managers: You multiply execution capacity. Stay close enough to see real constraints."
    ""
    "All senior leaders: Produce weekly evidence of progress."
    "   Distance from the work is not leadership. It is decay."
) | Out-Null

# SLIDE 33: Tensions and Open Questions
slide-content "Where the Model Has Friction: Tensions to Watch" @(
    "Open contribution vs. plan discipline"
    "   How is scope authority maintained when anyone can contribute to any repo?"
    ""
    "Named accountability vs. psychological safety"
    "   Explicit accountability can suppress speaking up when things go wrong"
    ""
    "Finite planning cycles vs. infinite mindset"
    "   How do you sequence and prioritize without treating cloud delivery as a project?"
    ""
    "Meritocracy vs. hierarchy"
    "   Who resolves disputes when contribution quality or priority is contested?"
    ""
    "Weekly proof gates vs. long-horizon work"
    "   What counts as evidence when the meaningful work spans months?"
    ""
    "These tensions don't invalidate the model — they are the implementation challenges."
) | Out-Null

# SLIDE 34: Call to Action
slide-content "Call to Action: What We Are Being Asked to Do" @(
    "1.  Define your mission team's scope, lead, metrics, and interfaces — this quarter, in writing, in a repo"
    ""
    "2.  Produce weekly evidence of progress — not narrative, not status updates — material evidence"
    ""
    "3.  Eliminate management by proxy — lean into standups, specs, code reviews, and failure modes"
    ""
    "4.  Embed AI in your delivery workflow now — it is a productivity multiplier, not a future investment"
    ""
    "5.  Adopt the operating model — iterate on it, but do not debate it endlessly"
    ""
    "'Delivery IS existential. Leaders make the difference. Let's execute together.  ON! ON!'"
) | Out-Null

# ==================================================================
# SAVE
# ==================================================================
$slideCount = $deck.Slides.Count
Write-Host "Saving $slideCount slides to: $outputPath"
$deck.SaveAs($outputPath, $ppSaveAsPPTX)
$deck.Close()
$pptApp.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($pptApp) | Out-Null
Write-Host "Done. $slideCount slides saved to: $outputPath"
