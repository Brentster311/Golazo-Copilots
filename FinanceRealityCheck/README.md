# Finance Planner

Local-first personal financial planning prototype focused on account ingestion, assisted categorization, budget alerts, portfolio-allocation planning guidance, and tax-aware threshold planning.

## Local development

1. Create and activate a virtual environment.
2. Install dependencies:
   - .\.venv\Scripts\python -m pip install -e .[dev]
3. Run tests:
   - .\.venv\Scripts\python -m pytest --cov=finance_planner --cov-report=term-missing

## Run the local API app

1. Start the server:
   - .\.venv\Scripts\python -m finance_planner.api --host 127.0.0.1 --port 8000
2. Verify health in a second terminal:
   - Invoke-RestMethod http://127.0.0.1:8000/health
3. Verify planner summary:
   - Invoke-RestMethod http://127.0.0.1:8000/planner/summary

## Run the local UI shell (FRC-006)

1. Open a second terminal and install frontend dependencies once:
   - Set-Location frontend
   - npm install
2. Start the frontend dev server:
   - npm run dev -- --host 127.0.0.1 --port 5173
3. Open the UI at:
   - http://127.0.0.1:5173
4. Verify deterministic UI contracts:
   - Health view shows status/version from `/health`
   - Planner Summary view shows capability list from `/planner/summary`
5. Run frontend automated tests:
   - npm run test

## Direct connector integration (FRC-007)

- Direct connector classes are available in `finance_planner.connectors`:
   - `FirstTechDirectConnector`
   - `FidelityDirectConnector`
- Direct connectors are intentionally disabled in `mode="test"`.
- Use non-test mode (for example `mode="live"`) to enable provider-backed authentication and sync fetches.
- `run_sync(days=90)` continues to enforce the 90-day ingestion window and duplicate-safe persistence behavior.

## Changelog

### 0.5.0 - 2026-05-11
- Added tax settings persistence for marginal rate, annual tax budget, and monthly withholding estimates.
- Added deterministic tax planning surface with YTD taxable income and annualized tax projections.
- Added budget-overrun and withholding-gap threshold alerts with actionable next steps.
- Added tests for tax settings validation, planning determinism, and threshold alerts.

### 0.4.0 - 2026-05-11
- Added local investment position persistence with upsert support.
- Added allocation dashboard output with per-asset-class percentages.
- Added target-allocation recommendation options that include suggested amounts plus explicit pros and cons.
- Added tests for allocation determinism, recommendation contract, and validation errors.

### 0.3.0 - 2026-05-10
- Added configurable unusual transaction detection with deterministic actionable alerts.
- Added savings goal tracking with contribution recording and goal-drift alerts.
- Added regression and feature tests covering alert and goal-drift behaviors.

### 0.1.1 - 2026-05-10
- Added local encrypted account and transaction persistence.
- Added fixture connector model for institution sync simulations.
- Added assisted categorization with user correction rule learning.
- Added monthly category-cap budget alerts.
- Added automated tests for ingestion, dedupe, categorization, budgets, and retry safety.
