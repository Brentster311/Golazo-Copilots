# TIM-0003: Concise 25-Minute Slide Deck — Tim's Delivery Vision
# 20 slides max, 3 bullets max per content slide
# Output: Tims-Delivery-Vision-Concise.pptx

$outputPath = "q:\src\Golazo-Copilots\TimsThoughts\WorkItems\TIM-0003\Tims-Delivery-Vision-Concise.pptx"

$ppLayoutTitle   = 1   # Centered title + subtitle
$ppLayoutContent = 2   # Title + content body
$ppSaveAsPPTX    = 24

$CR = [char]13

Write-Host "Starting PowerPoint..."
$pptApp = New-Object -ComObject PowerPoint.Application
$pptApp.Visible = 1
$deck = $pptApp.Presentations.Add(1)

function New-Slide($layout) {
    return $deck.Slides.Add($deck.Slides.Count + 1, $layout)
}
function ts($title, $sub) {
    $s = New-Slide $ppLayoutTitle
    $s.Shapes.Item(1).TextFrame.TextRange.Text = $title
    $s.Shapes.Item(2).TextFrame.TextRange.Text = $sub
    return $s
}
function tc($title, [string[]]$bullets) {
    $s = New-Slide $ppLayoutContent
    $s.Shapes.Item(1).TextFrame.TextRange.Text = $title
    $s.Shapes.Item(2).TextFrame.TextRange.Text = ($bullets -join "$CR")
    return $s
}

# SLIDE 1: Title
ts "Tim's Delivery Vision" "A 25-Minute Review of the Five-Document Corpus | April 2026" | Out-Null

# SLIDE 2: Corpus Abstract
tc "The Big Idea" @(
    "Delivery is now existential — not optional, not incremental. Organizations that cannot deliver continuously, safely, and at scale will lose."
    "The five documents build one coherent operating model: small accountable teams, infinite-game mindset, Harambee execution, and leaders who create clarity."
    "This is both a diagnosis of why we are failing and a prescription for how to operate differently."
) | Out-Null

# SLIDE 3: The Five Documents
tc "The Five Documents: A Progression" @(
    "Delivery is Existential — WHY delivery matters now (the urgency case)"
    "The Delivery Manifesto — HOW we will operate (the operating contract)   |   Delivery as Infinite Game — WHAT game we are playing (the mindset shift)"
    "Harambee and Mission Teams — WHO executes and how (the team model)   |   Senior IC Leader — WHO leads and how (the leadership model)"
) | Out-Null

# SLIDE 4: Cross-Doc Problem/Solution
tc "The Pattern Across All Five Documents" @(
    "Problem: Activity rewarded over outcomes; accountability diffuses into groups; finite mechanics applied to infinite systems"
    "Problem: Local optimization destroys systemic velocity; leaders too abstract or too local to produce clarity"
    "Solution: Named accountable leads | mission teams | steel threads | weekly material evidence | two-hat leaders who stay close to the work"
) | Out-Null

# ==== DOCUMENT 1 ====
ts "Delivery is Existential" "The Urgency Case" | Out-Null

tc "Delivery is Existential" @(
    "Problem: Slow delivery = existential risk; headcount grows as the default response; teams report activity rather than shipping material outcomes"
    "Gap: AI disruption and regulatory shifts (SFI, sovereign cloud) mean delivery speed is now a survival variable — not a lagging indicator reviewed quarterly"
    "Solution: Small accountable teams + earned headcount tied to demonstrated throughput + AI embedded across the full PM-Dev-Quality-Ops chain"
) | Out-Null

# ==== DOCUMENT 2 ====
ts "The Delivery Manifesto" "The Operating Contract" | Out-Null

tc "The Delivery Manifesto" @(
    "Problem: No single plan of record; blockers go unreported until they become crises; quality gated out at the end as a final check"
    "Gap: Multiple plans = nobody accountable; 'ownership' language without scope authority is performance theater; narrative without evidence accepted as progress"
    "Solution: Named lead per team | one visible plan of record | weekly proof gates (capability delivered, risk retired, integration completed) | silence = failure, escalation = leadership"
) | Out-Null

# ==== DOCUMENT 3 ====
ts "Delivery as an Infinite Game" "The Mindset Shift" | Out-Null

tc "Delivery as an Infinite Game" @(
    "Problem: Projects, temp teams, and fixed scopes applied to cloud and AI systems that live in production permanently and never stop evolving (regulations shift, threats adapt, models drift)"
    "Gap: Success defined as 'shipped it once' — not 'the system is healthier than last quarter'; PM treated as backlog operator, not strategic clarity engine"
    "Solution: Steel threads (durable, continuously exercised value streams) + product thinking (north stars, tradeoffs, health signals) + no finish line"
) | Out-Null

# ==== DOCUMENT 4 ====
ts "Harambee and Mission Teams" "The Team Model" | Out-Null

tc "Harambee and Mission Teams" @(
    "Problem: Local optimization destroys systemic velocity; dependencies discovered at integration time rather than at design time"
    "Gap: Escalation is the default cross-team mechanism — too slow, creates bottlenecks, and destroys accountability at the boundaries"
    "Solution: Harambee — all pull together | every team: named lead + mission + metrics + interfaces + dependencies | composition by default; direct contribution over escalation"
) | Out-Null

# ==== DOCUMENT 5 ====
ts "The Role of the Senior IC Leader" "The Leadership Model" | Out-Null

tc "The Role of the Senior IC Leader" @(
    "Problem: Leaders too abstract (coordination theater) or too local (optimize without seeing system); ambiguity is a leadership product, not a team problem"
    "Gap: PMs as traffic controllers, Architects as review boards, EMs as people-only managers — clarity never gets produced"
    "Solution: Two hats always (IC depth + leadership judgment) | hands-on proximity to the work | PM = clarity engine | Architect = coherence guardian | EM = execution multiplier"
) | Out-Null

# ==== SYNTHESIS ====

# SLIDE 15
tc "Five Documents, Five Consistent Signals" @(
    "1. Accountability must be explicit and named — not inferred, not collective   2. Small teams with clear scope outperform large diffuse teams"
    "3. Material evidence replaces activity narrative — weekly, visible, no exceptions   4. AI is a productivity multiplier — not adopting it is falling behind by choice"
    "5. Leaders create clarity and maintain execution proximity — or they fail the team and the system"
) | Out-Null

# SLIDE 16
tc "The Accountability Architecture (How the Model Layers)" @(
    "Individual: two-hat senior IC leader — IC depth + leadership judgment + hands-on proximity to the work"
    "Team: mission team = named lead + explicit scope + success metrics + defined interfaces + known dependencies"
    "System: steel threads + product thinking + infinite-game orientation — bound together by Harambee across all boundaries"
) | Out-Null

# SLIDE 17
tc "What This Means for You: By Role" @(
    "PMs: Write intent, outcomes, and tradeoffs in repos — not email, not pptx. You are a clarity engine, not a traffic controller."
    "Architects and Tech Leads: Define steel threads. Hold invariants. Surface risk early — do not absorb it silently."
    "Engineering Managers: Stay close enough to see real constraints. Distance is not leadership. It is decay."
) | Out-Null

# SLIDE 18
tc "Tensions the Model Must Navigate" @(
    "Open contribution vs. plan discipline — how is scope authority maintained when anyone can contribute to any repo?"
    "Named accountability vs. psychological safety — explicit accountability can suppress speaking up when things go wrong"
    "Weekly proof gates vs. long-horizon work — what counts as material evidence when the meaningful work spans months?"
) | Out-Null

# SLIDE 19
tc "Call to Action" @(
    "Define your mission team's scope, lead, metrics, and interfaces — this quarter, in writing, in a repo"
    "Produce weekly evidence of progress — not narrative, not status updates — material, visible evidence"
    "Embed AI in your delivery workflow now. Lean into the work. Adopt the model."
) | Out-Null

# SLIDE 20: Closing Quote
ts `
    "'Delivery IS existential. Leaders make the difference.'" `
    "Let's execute together.  ON! ON!" | Out-Null

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
