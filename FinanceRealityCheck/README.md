# Finance Planner

Local-first personal financial planning prototype focused on account ingestion, assisted categorization, and budget alerts.

## Local development

1. Create and activate a virtual environment.
2. Install dependencies:
   - .\.venv\Scripts\python -m pip install -e .[dev]
3. Run tests:
   - .\.venv\Scripts\python -m pytest --cov=finance_planner --cov-report=term-missing

## Changelog

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
