# FRC-015 Project Owner Assistant Notes

## Scope decision
Prioritize unsafe-spending habit warnings that are grounded in realistic baseline behavior, not raw debit spikes.

## Why this story exists
User goal is behavior safety: detect when ongoing spend pace becomes risky before month end, with actionable and explainable reasons.

## Dependencies
- Spend classification and baseline outputs from FRC-014.
- Existing alert surfaces and local planner persistence from FRC-002 and current planner service.
