# SFI Reporter

### Eliminating SFI Toil — One Click at a Time

> Built end-to-end in just a few days using **Golazo Copilot**, an AI-assisted development workflow.

---

## The Problem

Engineers managing SFI/QEI remediation spend hours each week on repetitive, manual work:

- Logging into the S360 portal and clicking through each service one at a time
- Manually checking which action items have stale or missing ETAs
- Copy-pasting KPI details to figure out what actually needs to be fixed
- Updating ETAs individually — one form submission per item
- No easy way to see the full picture across services, KPIs, and owners

**This is toil.** It doesn't require judgment — it requires automation.

---

## Visibility & Control

### See Everything in One Place

- **Single window** shows all SFI/QEI action items across every service you own
- **Drill-down views** by service, KPI, program, or action owner — no portal navigation
- **Color-coded SLA status** — instantly see what's In SLA, Approaching, or Out of SLA
- **Customizable columns** — show only the data you care about; hides empty fields automatically

### Filter & Find Fast

- **Built-in query builder** — filter by Service Name, Assigned To, Program, Due Date, ETA Date
- **Persistent filters** — your clauses are saved between sessions, no re-entry
- **Detail modals** — click any row for the full action item breakdown

### Zero Setup for End Users

- Download **SFIReporter.exe**, double-click, done — no Python, no dev tools
- Signs in automatically using your existing Azure session, or opens a browser prompt

---

## Automation & AI

### Bulk ETA Updates — Minutes, Not Hours

- **Auto-fix mode** — one click to propose and apply valid ETAs for every stale item
- **Manual review mode** — step through items one by one with full detail view
- **Scoped updates** — multi-select rows in any drill-down and update just those
- **Validation built in** — dates must be today or later, within one year, proper format

### AI-Powered Remediation Analysis

- **Right-click any KPI** → sends item data to Azure OpenAI for a structured analysis:
  - **Mission** — what is being asked
  - **Steps to Done** — actionable numbered plan
  - **Resources Needing Repair** — specific assets, subscriptions, tenants
  - **Risk of Delay** — SLA impact and compliance consequences
- Results saved locally for offline reference and sharing

### Real Impact

| Before | After |
|--------|-------|
| 30+ min to review items across services | Seconds — one window, all services |
| Manual ETA updates, one at a time | Bulk update dozens of items in one click |
| Read raw KPI data and guess next steps | AI generates a remediation plan on demand |

---

## How It Was Built

### AI-Assisted Development with Golazo Copilot

The entire SFI Reporter — SDK, desktop app, LLM integration, packaging — was built in **just a few days** using **Golazo Copilot**, a structured AI development workflow.

**What Golazo Copilot provided:**

- **Role-based workflow** — each phase (design, architecture, dev, QA, docs) has guardrails
- **Automatic gate enforcement** — can't skip ahead; design docs must exist before code
- **Capability registry** — 25 tracked capabilities with dependency mapping and impact analysis
- **Consistent quality** — every feature went through the same structured pipeline

**What this means for the org:**

- Repeatable pattern for building internal tools fast
- AI handles the boilerplate; engineers focus on domain logic
- Days instead of weeks for a fully tested, packaged desktop app
