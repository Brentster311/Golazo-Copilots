from __future__ import annotations

import json
import sqlite3
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from statistics import mean, pstdev
from typing import Any

from cryptography.fernet import Fernet

from .connectors import ConnectorError, FixtureConnector, TransactionRecord


class PlannerValidationError(ValueError):
    pass


class FinancialPlannerService:
    def __init__(
        self,
        db_path: Path | str,
        key_path: Path | str,
        connectors: dict[str, FixtureConnector],
    ) -> None:
        self._db_path = Path(db_path)
        self._key_path = Path(key_path)
        self._connectors = connectors

        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._key_path.parent.mkdir(parents=True, exist_ok=True)

        self._fernet = Fernet(self._load_or_create_key())
        self._connection = sqlite3.connect(self._db_path)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA foreign_keys = ON;")
        self._ensure_schema()

    def close(self) -> None:
        if hasattr(self, "_connection") and self._connection is not None:
            self._connection.close()
            self._connection = None

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass

    def link_account(self, institution: str, display_name: str, access_token: str) -> int:
        if institution not in self._connectors:
            raise PlannerValidationError(f"No connector configured for institution: {institution}")
        if not display_name.strip():
            raise PlannerValidationError("display_name cannot be empty")
        if not access_token.strip():
            raise PlannerValidationError("access_token cannot be empty")

        cursor = self._connection.execute(
            """
            INSERT INTO accounts (institution, display_name, access_token)
            VALUES (?, ?, ?)
            """,
            (institution, display_name.strip(), self._encrypt_text(access_token.strip())),
        )
        self._connection.commit()
        return int(cursor.lastrowid)

    def update_account_access_token(self, account_id: int, access_token: str) -> None:
        if not access_token.strip():
            raise PlannerValidationError("access_token cannot be empty")

        cursor = self._connection.execute(
            "UPDATE accounts SET access_token = ? WHERE id = ?",
            (self._encrypt_text(access_token.strip()), account_id),
        )
        if cursor.rowcount == 0:
            raise PlannerValidationError(f"Unknown account id: {account_id}")
        self._connection.commit()

    def run_sync(self, days: int = 90) -> dict[str, Any]:
        if days <= 0:
            raise PlannerValidationError("days must be greater than zero")

        cutoff = datetime.now(tz=UTC) - timedelta(days=days)
        account_rows = self._connection.execute(
            "SELECT id, institution, display_name, access_token FROM accounts ORDER BY id"
        ).fetchall()

        account_results: list[dict[str, Any]] = []
        duplicates_skipped_total = 0

        for account in account_rows:
            result: dict[str, Any] = {
                "account_id": account["id"],
                "institution": account["institution"],
                "account": account["display_name"],
            }

            connector = self._connectors.get(account["institution"])
            if connector is None:
                result.update(
                    {
                        "status": "failed",
                        "error_category": "connector_missing",
                        "actionable_message": "No connector configured for institution. Add connector and retry sync.",
                    }
                )
                account_results.append(result)
                continue

            try:
                access_token = self._decrypt_text(account["access_token"])
                fetched = connector.fetch_transactions(access_token=access_token, start_at=cutoff)
                imported_count, duplicates_skipped = self._store_transactions(account["id"], fetched)

                duplicates_skipped_total += duplicates_skipped
                result.update(
                    {
                        "status": "success",
                        "imported_count": imported_count,
                        "duplicates_skipped": duplicates_skipped,
                    }
                )
            except ConnectorError as error:
                result.update(
                    {
                        "status": "failed",
                        "error_category": error.category,
                        "actionable_message": error.actionable_message,
                    }
                )
            except Exception:
                result.update(
                    {
                        "status": "failed",
                        "error_category": "storage_error",
                        "actionable_message": "Unexpected storage error occurred. Retry sync after reviewing local logs.",
                    }
                )

            account_results.append(result)

        self._connection.commit()

        statuses = [item["status"] for item in account_results]
        if statuses and all(status == "success" for status in statuses):
            overall_status = "success"
        elif any(status == "success" for status in statuses):
            overall_status = "partial_failure"
        else:
            overall_status = "failed"

        return {
            "overall_status": overall_status,
            "account_results": account_results,
            "duplicates_skipped": duplicates_skipped_total,
        }

    def list_transactions(self) -> list[dict[str, Any]]:
        rows = self._connection.execute(
            """
            SELECT
                t.id,
                t.provider_transaction_id,
                t.posted_on,
                t.amount,
                t.merchant,
                a.display_name AS account,
                t.direction,
                t.category,
                t.category_source
            FROM transactions t
            INNER JOIN accounts a ON a.id = t.account_id
            ORDER BY t.posted_on, t.id
            """
        ).fetchall()

        return [dict(row) for row in rows]

    def get_raw_encrypted_payload(self, transaction_id: int) -> bytes:
        row = self._connection.execute(
            "SELECT encrypted_payload FROM transactions WHERE id = ?",
            (transaction_id,),
        ).fetchone()
        if row is None:
            raise PlannerValidationError(f"Unknown transaction id: {transaction_id}")
        return bytes(row["encrypted_payload"])

    def confirm_category(self, transaction_id: int, category: str) -> None:
        cleaned_category = category.strip()
        if not cleaned_category:
            raise PlannerValidationError("category cannot be empty")

        row = self._connection.execute(
            "SELECT merchant FROM transactions WHERE id = ?",
            (transaction_id,),
        ).fetchone()
        if row is None:
            raise PlannerValidationError(f"Unknown transaction id: {transaction_id}")

        normalized_merchant = self._normalize_merchant(row["merchant"])

        self._connection.execute(
            "UPDATE transactions SET category = ?, category_source = 'manual' WHERE id = ?",
            (cleaned_category, transaction_id),
        )
        self._connection.execute(
            """
            INSERT INTO category_rules (normalized_merchant, category)
            VALUES (?, ?)
            ON CONFLICT(normalized_merchant)
            DO UPDATE SET category = excluded.category
            """,
            (normalized_merchant, cleaned_category),
        )
        self._connection.commit()

    def set_budget(self, category: str, monthly_cap: float) -> None:
        cleaned_category = category.strip()
        if not cleaned_category:
            raise PlannerValidationError("category cannot be empty")
        if monthly_cap < 0:
            raise PlannerValidationError("monthly_cap cannot be negative")

        self._connection.execute(
            """
            INSERT INTO budgets (category, monthly_cap)
            VALUES (?, ?)
            ON CONFLICT(category)
            DO UPDATE SET monthly_cap = excluded.monthly_cap
            """,
            (cleaned_category, float(monthly_cap)),
        )
        self._connection.commit()

    def get_budget_alerts(self, year: int, month: int) -> list[dict[str, Any]]:
        if month < 1 or month > 12:
            raise PlannerValidationError("month must be between 1 and 12")

        period_start = date(year, month, 1)
        period_end = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)

        spent_rows = self._connection.execute(
            """
            SELECT category, COALESCE(SUM(amount), 0) AS spent
            FROM transactions
            WHERE direction = 'debit'
              AND category IS NOT NULL
              AND posted_on >= ?
              AND posted_on < ?
            GROUP BY category
            """,
            (period_start.isoformat(), period_end.isoformat()),
        ).fetchall()
        spent_by_category = {row["category"]: float(row["spent"]) for row in spent_rows}

        budget_rows = self._connection.execute(
            "SELECT category, monthly_cap FROM budgets ORDER BY category"
        ).fetchall()

        alerts: list[dict[str, Any]] = []
        for row in budget_rows:
            category = row["category"]
            cap = float(row["monthly_cap"])
            spent = spent_by_category.get(category, 0.0)
            if spent > cap:
                alerts.append(
                    {
                        "category": category,
                        "cap": cap,
                        "spent": spent,
                        "year": year,
                        "month": month,
                    }
                )

        return alerts

    def update_unusual_settings(self, minimum_amount: float, sensitivity_factor: float, min_samples: int = 3) -> None:
        if minimum_amount < 0:
            raise PlannerValidationError("minimum_amount cannot be negative")
        if sensitivity_factor <= 0:
            raise PlannerValidationError("sensitivity_factor must be greater than zero")
        if min_samples < 1:
            raise PlannerValidationError("min_samples must be at least 1")

        self._connection.execute(
            """
            INSERT INTO alert_settings (id, minimum_amount, sensitivity_factor, min_samples)
            VALUES (1, ?, ?, ?)
            ON CONFLICT(id)
            DO UPDATE SET
                minimum_amount = excluded.minimum_amount,
                sensitivity_factor = excluded.sensitivity_factor,
                min_samples = excluded.min_samples,
                updated_at = CURRENT_TIMESTAMP
            """,
            (float(minimum_amount), float(sensitivity_factor), int(min_samples)),
        )
        self._connection.commit()

    def get_unusual_settings(self) -> dict[str, Any]:
        row = self._connection.execute(
            "SELECT minimum_amount, sensitivity_factor, min_samples FROM alert_settings WHERE id = 1"
        ).fetchone()
        if row is None:
            settings = {
                "minimum_amount": 100.0,
                "sensitivity_factor": 2.0,
                "min_samples": 3,
            }
            self.update_unusual_settings(**settings)
            return settings

        return {
            "minimum_amount": float(row["minimum_amount"]),
            "sensitivity_factor": float(row["sensitivity_factor"]),
            "min_samples": int(row["min_samples"]),
        }

    def get_unusual_transaction_alerts(self, days: int = 90) -> list[dict[str, Any]]:
        if days <= 0:
            raise PlannerValidationError("days must be greater than zero")

        settings = self.get_unusual_settings()
        cutoff = datetime.now(tz=UTC).date() - timedelta(days=days)

        rows = self._connection.execute(
            """
            SELECT id, provider_transaction_id, posted_on, amount, merchant, category
            FROM transactions
            WHERE direction = 'debit'
              AND posted_on >= ?
            ORDER BY posted_on, id
            """,
            (cutoff.isoformat(),),
        ).fetchall()

        alerts: list[dict[str, Any]] = []
        for row in rows:
            amount = float(row["amount"])
            if amount < settings["minimum_amount"]:
                continue

            normalized_merchant = self._normalize_merchant(str(row["merchant"]))
            baseline_rows = self._connection.execute(
                """
                SELECT amount
                FROM transactions
                WHERE direction = 'debit'
                  AND lower(trim(merchant)) = ?
                  AND posted_on < ?
                ORDER BY posted_on DESC, id DESC
                LIMIT 50
                """,
                (normalized_merchant, row["posted_on"]),
            ).fetchall()

            baseline_values = [float(item["amount"]) for item in baseline_rows]
            if len(baseline_values) < settings["min_samples"]:
                continue

            avg_amount = mean(baseline_values)
            spread = pstdev(baseline_values) if len(baseline_values) > 1 else 0.0
            spread_floor = max(spread, avg_amount * 0.25)
            threshold = max(
                settings["minimum_amount"],
                avg_amount + (settings["sensitivity_factor"] * spread_floor),
            )

            if amount <= threshold:
                continue

            severity = "high" if amount >= threshold * 1.5 else "medium"
            alerts.append(
                {
                    "alert_type": "unusual_transaction",
                    "transaction_id": int(row["id"]),
                    "provider_transaction_id": row["provider_transaction_id"],
                    "merchant": row["merchant"],
                    "amount": amount,
                    "threshold": round(threshold, 2),
                    "baseline_samples": len(baseline_values),
                    "reason": "amount exceeds recent merchant spending baseline",
                    "severity": severity,
                    "next_step": "Review the transaction and confirm whether it is expected.",
                }
            )

        return alerts

    def create_savings_goal(
        self,
        name: str,
        target_amount: float,
        target_date: date,
        monthly_contribution: float,
    ) -> int:
        cleaned_name = name.strip()
        if not cleaned_name:
            raise PlannerValidationError("goal name cannot be empty")
        if target_amount <= 0:
            raise PlannerValidationError("target_amount must be greater than zero")
        if target_date <= date.today():
            raise PlannerValidationError("target_date must be in the future")
        if monthly_contribution <= 0:
            raise PlannerValidationError("monthly_contribution must be greater than zero")

        cursor = self._connection.execute(
            """
            INSERT INTO savings_goals (name, target_amount, target_date, monthly_contribution, created_on)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                cleaned_name,
                float(target_amount),
                target_date.isoformat(),
                float(monthly_contribution),
                date.today().isoformat(),
            ),
        )
        self._connection.commit()
        return int(cursor.lastrowid)

    def add_goal_contribution(self, goal_id: int, amount: float, contributed_on: date | None = None) -> None:
        if amount <= 0:
            raise PlannerValidationError("contribution amount must be greater than zero")

        goal = self._connection.execute(
            "SELECT id FROM savings_goals WHERE id = ?",
            (goal_id,),
        ).fetchone()
        if goal is None:
            raise PlannerValidationError(f"Unknown goal id: {goal_id}")

        contribution_date = contributed_on or date.today()
        self._connection.execute(
            """
            INSERT INTO goal_contributions (goal_id, amount, contributed_on)
            VALUES (?, ?, ?)
            """,
            (goal_id, float(amount), contribution_date.isoformat()),
        )
        self._connection.commit()

    def get_goal_drift_alerts(self, as_of: date | None = None) -> list[dict[str, Any]]:
        anchor_date = as_of or date.today()
        goals = self._connection.execute(
            """
            SELECT id, name, target_amount, target_date, monthly_contribution, created_on
            FROM savings_goals
            WHERE active = 1
            ORDER BY id
            """
        ).fetchall()

        alerts: list[dict[str, Any]] = []
        for goal in goals:
            created_on = date.fromisoformat(goal["created_on"])
            target_date = date.fromisoformat(goal["target_date"])
            if anchor_date <= created_on:
                continue

            total_days = max((target_date - created_on).days, 1)
            elapsed_days = min(max((anchor_date - created_on).days, 0), total_days)

            target_amount = float(goal["target_amount"])
            monthly_contribution = float(goal["monthly_contribution"])

            expected_linear = target_amount * (elapsed_days / total_days)
            expected_monthly = monthly_contribution * (elapsed_days / 30.0)
            expected_to_date = min(target_amount, max(expected_linear, expected_monthly))

            contribution_row = self._connection.execute(
                """
                SELECT COALESCE(SUM(amount), 0) AS total
                FROM goal_contributions
                WHERE goal_id = ?
                  AND contributed_on <= ?
                """,
                (goal["id"], anchor_date.isoformat()),
            ).fetchone()
            actual_to_date = float(contribution_row["total"])
            deficit = expected_to_date - actual_to_date

            if deficit <= 0:
                continue

            severity = "high" if deficit >= monthly_contribution else "medium"
            alerts.append(
                {
                    "alert_type": "goal_drift",
                    "goal_id": int(goal["id"]),
                    "goal_name": goal["name"],
                    "expected_to_date": round(expected_to_date, 2),
                    "actual_to_date": round(actual_to_date, 2),
                    "deficit": round(deficit, 2),
                    "severity": severity,
                    "reason": "saved amount is behind expected pace for target date",
                    "next_step": "Increase monthly contribution or adjust goal timeline.",
                }
            )

        return alerts

    def upsert_investment_position(
        self,
        symbol: str,
        asset_class: str,
        account_label: str,
        market_value: float,
    ) -> int:
        cleaned_symbol = symbol.strip().upper()
        cleaned_asset_class = asset_class.strip()
        cleaned_account_label = account_label.strip()

        if not cleaned_symbol:
            raise PlannerValidationError("symbol cannot be empty")
        if not cleaned_asset_class:
            raise PlannerValidationError("asset_class cannot be empty")
        if not cleaned_account_label:
            raise PlannerValidationError("account_label cannot be empty")
        if market_value <= 0:
            raise PlannerValidationError("market_value must be greater than zero")

        self._connection.execute(
            """
            INSERT INTO investment_positions (symbol, asset_class, account_label, market_value)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(symbol, account_label)
            DO UPDATE SET
                asset_class = excluded.asset_class,
                market_value = excluded.market_value,
                updated_at = CURRENT_TIMESTAMP
            """,
            (cleaned_symbol, cleaned_asset_class, cleaned_account_label, float(market_value)),
        )
        row = self._connection.execute(
            "SELECT id FROM investment_positions WHERE symbol = ? AND account_label = ?",
            (cleaned_symbol, cleaned_account_label),
        ).fetchone()
        self._connection.commit()

        if row is None:
            raise PlannerValidationError("Unable to persist investment position")
        return int(row["id"])

    def list_investment_positions(self) -> list[dict[str, Any]]:
        rows = self._connection.execute(
            """
            SELECT id, symbol, asset_class, account_label, market_value
            FROM investment_positions
            ORDER BY asset_class, symbol, account_label, id
            """
        ).fetchall()

        return [
            {
                "id": int(row["id"]),
                "symbol": row["symbol"],
                "asset_class": row["asset_class"],
                "account_label": row["account_label"],
                "market_value": float(row["market_value"]),
            }
            for row in rows
        ]

    def get_allocation_dashboard(self) -> dict[str, Any]:
        rows = self._connection.execute(
            """
            SELECT asset_class, SUM(market_value) AS market_value
            FROM investment_positions
            GROUP BY asset_class
            ORDER BY asset_class
            """
        ).fetchall()

        total_market_value = sum(float(row["market_value"]) for row in rows)

        allocations: list[dict[str, Any]] = []
        for row in rows:
            market_value = float(row["market_value"])
            percentage = 0.0 if total_market_value == 0 else (market_value / total_market_value) * 100.0
            allocations.append(
                {
                    "asset_class": row["asset_class"],
                    "market_value": round(market_value, 2),
                    "percentage": round(percentage, 2),
                }
            )

        return {
            "total_market_value": round(total_market_value, 2),
            "allocations": allocations,
        }

    def get_allocation_recommendations(
        self,
        target_allocations: dict[str, float],
        tolerance: float = 0.05,
    ) -> list[dict[str, Any]]:
        if not target_allocations:
            raise PlannerValidationError("target_allocations cannot be empty")
        if tolerance <= 0:
            raise PlannerValidationError("tolerance must be greater than zero")

        cleaned_targets: dict[str, float] = {}
        for asset_class, target in target_allocations.items():
            cleaned_asset_class = asset_class.strip()
            if not cleaned_asset_class:
                raise PlannerValidationError("target allocation asset_class cannot be empty")
            if target <= 0 or target > 1:
                raise PlannerValidationError("target allocation values must be between 0 and 1")
            cleaned_targets[cleaned_asset_class] = float(target)

        total_target = sum(cleaned_targets.values())
        if abs(total_target - 1.0) > 0.001:
            raise PlannerValidationError("target allocation values must sum to 1.0")

        dashboard = self.get_allocation_dashboard()
        total_market_value = float(dashboard["total_market_value"])
        current_values = {
            item["asset_class"]: float(item["market_value"])
            for item in dashboard["allocations"]
        }

        covered_classes = sorted(set(current_values.keys()) | set(cleaned_targets.keys()))
        recommendation_rows: list[dict[str, Any]] = []

        for asset_class in covered_classes:
            target_fraction = cleaned_targets.get(asset_class, 0.0)
            current_fraction = 0.0
            if total_market_value > 0:
                current_fraction = current_values.get(asset_class, 0.0) / total_market_value

            drift = current_fraction - target_fraction
            if abs(drift) <= tolerance:
                continue

            direction = "decrease" if drift > 0 else "increase"
            suggested_amount = abs(drift) * total_market_value

            if suggested_amount <= 0:
                continue

            if direction == "increase":
                pros = [
                    "Moves portfolio toward target diversification.",
                    "Reduces under-allocation risk for this asset class.",
                ]
                cons = [
                    "May underperform if this asset class lags in the near term.",
                    "Can increase short-term allocation volatility.",
                ]
            else:
                pros = [
                    "Lowers concentration risk in an overweight asset class.",
                    "Improves balance against long-term targets.",
                ]
                cons = [
                    "May limit upside if the current asset class continues to lead.",
                    "Could increase tracking error against recent performance trends.",
                ]

            recommendation_rows.append(
                {
                    "asset_class": asset_class,
                    "direction": direction,
                    "current_percentage": round(current_fraction * 100.0, 2),
                    "target_percentage": round(target_fraction * 100.0, 2),
                    "suggested_amount": round(suggested_amount, 2),
                    "summary": (
                        f"Consider {direction} exposure to {asset_class} by approximately "
                        f"${suggested_amount:.2f} to move closer to target allocation."
                    ),
                    "pros": pros,
                    "cons": cons,
                }
            )

        recommendation_rows.sort(
            key=lambda item: (
                -abs(item["current_percentage"] - item["target_percentage"]),
                item["asset_class"],
            )
        )
        return recommendation_rows

    def update_tax_settings(
        self,
        marginal_tax_rate: float,
        annual_tax_budget: float,
        monthly_withholding: float,
    ) -> None:
        if marginal_tax_rate <= 0 or marginal_tax_rate > 1:
            raise PlannerValidationError("marginal_tax_rate must be between 0 and 1")
        if annual_tax_budget <= 0:
            raise PlannerValidationError("annual_tax_budget must be greater than zero")
        if monthly_withholding <= 0:
            raise PlannerValidationError("monthly_withholding must be greater than zero")

        self._connection.execute(
            """
            INSERT INTO tax_settings (id, marginal_tax_rate, annual_tax_budget, monthly_withholding)
            VALUES (1, ?, ?, ?)
            ON CONFLICT(id)
            DO UPDATE SET
                marginal_tax_rate = excluded.marginal_tax_rate,
                annual_tax_budget = excluded.annual_tax_budget,
                monthly_withholding = excluded.monthly_withholding,
                updated_at = CURRENT_TIMESTAMP
            """,
            (float(marginal_tax_rate), float(annual_tax_budget), float(monthly_withholding)),
        )
        self._connection.commit()

    def get_tax_settings(self) -> dict[str, Any]:
        row = self._connection.execute(
            "SELECT marginal_tax_rate, annual_tax_budget, monthly_withholding FROM tax_settings WHERE id = 1"
        ).fetchone()
        if row is None:
            defaults = {
                "marginal_tax_rate": 0.22,
                "annual_tax_budget": 5000.0,
                "monthly_withholding": 300.0,
            }
            self.update_tax_settings(**defaults)
            return defaults

        return {
            "marginal_tax_rate": float(row["marginal_tax_rate"]),
            "annual_tax_budget": float(row["annual_tax_budget"]),
            "monthly_withholding": float(row["monthly_withholding"]),
        }

    def get_tax_planning_surface(self, as_of: date | None = None) -> dict[str, Any]:
        anchor_date = as_of or date.today()
        start_of_year = date(anchor_date.year, 1, 1)
        days_elapsed = max((anchor_date - start_of_year).days + 1, 1)

        row = self._connection.execute(
            """
            SELECT COALESCE(SUM(amount), 0) AS taxable_income
            FROM transactions
            WHERE direction = 'credit'
              AND posted_on >= ?
              AND posted_on <= ?
            """,
            (start_of_year.isoformat(), anchor_date.isoformat()),
        ).fetchone()

        ytd_taxable_income = float(row["taxable_income"])
        settings = self.get_tax_settings()

        projected_annual_income = ytd_taxable_income * (365.0 / float(days_elapsed))
        projected_annual_tax = projected_annual_income * settings["marginal_tax_rate"]
        projected_annual_withholding = settings["monthly_withholding"] * 12.0

        return {
            "year": anchor_date.year,
            "as_of": anchor_date.isoformat(),
            "days_elapsed": days_elapsed,
            "ytd_taxable_income": round(ytd_taxable_income, 2),
            "projected_annual_income": round(projected_annual_income, 2),
            "marginal_tax_rate": round(settings["marginal_tax_rate"], 4),
            "projected_annual_tax": round(projected_annual_tax, 2),
            "annual_tax_budget": round(settings["annual_tax_budget"], 2),
            "monthly_withholding": round(settings["monthly_withholding"], 2),
            "projected_annual_withholding": round(projected_annual_withholding, 2),
        }

    def get_tax_threshold_alerts(self, as_of: date | None = None) -> list[dict[str, Any]]:
        surface = self.get_tax_planning_surface(as_of=as_of)

        projected_annual_tax = float(surface["projected_annual_tax"])
        annual_tax_budget = float(surface["annual_tax_budget"])
        projected_annual_withholding = float(surface["projected_annual_withholding"])
        monthly_withholding = float(surface["monthly_withholding"])

        alerts: list[dict[str, Any]] = []

        if projected_annual_tax > annual_tax_budget:
            overrun = projected_annual_tax - annual_tax_budget
            ratio = projected_annual_tax / annual_tax_budget if annual_tax_budget > 0 else 1.0
            severity = "high" if ratio >= 1.25 else "medium"
            alerts.append(
                {
                    "alert_type": "budget_overrun",
                    "severity": severity,
                    "projected_annual_tax": round(projected_annual_tax, 2),
                    "annual_tax_budget": round(annual_tax_budget, 2),
                    "overrun_amount": round(overrun, 2),
                    "reason": "projected annual tax exceeds configured annual budget threshold",
                    "next_step": "Increase tax reserve contributions or adjust annual tax budget assumptions.",
                }
            )

        if projected_annual_tax > projected_annual_withholding:
            gap = projected_annual_tax - projected_annual_withholding
            severity = "high" if gap >= (monthly_withholding * 3.0) else "medium"
            alerts.append(
                {
                    "alert_type": "withholding_gap",
                    "severity": severity,
                    "projected_annual_tax": round(projected_annual_tax, 2),
                    "projected_annual_withholding": round(projected_annual_withholding, 2),
                    "gap_amount": round(gap, 2),
                    "reason": "projected annual tax exceeds projected annual withholding",
                    "next_step": "Increase withholding estimate or set aside additional monthly tax savings.",
                }
            )

        alerts.sort(key=lambda item: item["alert_type"])
        return alerts

    def _store_transactions(self, account_id: int, transactions: list[TransactionRecord]) -> tuple[int, int]:
        imported_count = 0
        duplicates_skipped = 0

        for record in transactions:
            normalized_merchant = self._normalize_merchant(record.merchant)
            category, category_source = self._resolve_category(normalized_merchant, record.direction)
            payload = {
                "provider_transaction_id": record.provider_transaction_id,
                "posted_at": record.posted_at.isoformat(),
                "amount": float(record.amount),
                "merchant": record.merchant,
                "direction": record.direction,
            }

            try:
                self._connection.execute(
                    """
                    INSERT INTO transactions (
                        account_id,
                        provider_transaction_id,
                        posted_on,
                        amount,
                        merchant,
                        direction,
                        encrypted_payload,
                        category,
                        category_source
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        account_id,
                        record.provider_transaction_id,
                        record.posted_at.astimezone(UTC).date().isoformat(),
                        float(record.amount),
                        record.merchant,
                        self._sanitize_direction(record.direction),
                        self._encrypt_payload(payload),
                        category,
                        category_source,
                    ),
                )
                imported_count += 1
            except sqlite3.IntegrityError:
                duplicates_skipped += 1

        return imported_count, duplicates_skipped

    def _resolve_category(self, normalized_merchant: str, direction: str) -> tuple[str | None, str]:
        row = self._connection.execute(
            "SELECT category FROM category_rules WHERE normalized_merchant = ?",
            (normalized_merchant,),
        ).fetchone()
        if row is not None:
            return str(row["category"]), "rule"

        heuristic = self._heuristic_category(normalized_merchant, direction)
        if heuristic is not None:
            return heuristic, "heuristic"

        return None, "uncategorized"

    @staticmethod
    def _normalize_merchant(merchant: str) -> str:
        return " ".join(merchant.strip().lower().split())

    @staticmethod
    def _heuristic_category(normalized_merchant: str, direction: str) -> str | None:
        if direction.strip().lower() == "credit":
            if "payroll" in normalized_merchant or "deposit" in normalized_merchant:
                return "Income"
            return None

        keyword_map = {
            "rent": "Housing",
            "grocery": "Groceries",
            "coffee": "Dining",
            "restaurant": "Dining",
            "fuel": "Transportation",
            "gas": "Transportation",
            "utility": "Utilities",
            "power": "Utilities",
            "stream": "Entertainment",
            "entertain": "Entertainment",
        }
        for keyword, category in keyword_map.items():
            if keyword in normalized_merchant:
                return category
        return None

    @staticmethod
    def _sanitize_direction(direction: str) -> str:
        normalized = direction.strip().lower()
        if normalized in {"debit", "credit"}:
            return normalized
        return "debit"

    def _load_or_create_key(self) -> bytes:
        if self._key_path.exists():
            return self._key_path.read_bytes().strip()

        key = Fernet.generate_key()
        self._key_path.write_bytes(key)
        return key

    def _encrypt_payload(self, payload: dict[str, Any]) -> bytes:
        raw = json.dumps(payload, sort_keys=True).encode("utf-8")
        return self._fernet.encrypt(raw)

    def _encrypt_text(self, value: str) -> bytes:
        return self._fernet.encrypt(value.encode("utf-8"))

    def _decrypt_text(self, encrypted: bytes) -> str:
        return self._fernet.decrypt(bytes(encrypted)).decode("utf-8")

    def _ensure_schema(self) -> None:
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                institution TEXT NOT NULL,
                display_name TEXT NOT NULL,
                access_token BLOB NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                provider_transaction_id TEXT NOT NULL,
                posted_on TEXT NOT NULL,
                amount REAL NOT NULL,
                merchant TEXT NOT NULL,
                direction TEXT NOT NULL,
                encrypted_payload BLOB NOT NULL,
                category TEXT,
                category_source TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(account_id, provider_transaction_id),
                FOREIGN KEY(account_id) REFERENCES accounts(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS category_rules (
                normalized_merchant TEXT PRIMARY KEY,
                category TEXT NOT NULL,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS budgets (
                category TEXT PRIMARY KEY,
                monthly_cap REAL NOT NULL,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS alert_settings (
                id INTEGER PRIMARY KEY CHECK(id = 1),
                minimum_amount REAL NOT NULL,
                sensitivity_factor REAL NOT NULL,
                min_samples INTEGER NOT NULL,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS savings_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                target_amount REAL NOT NULL,
                target_date TEXT NOT NULL,
                monthly_contribution REAL NOT NULL,
                created_on TEXT NOT NULL,
                active INTEGER NOT NULL DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS goal_contributions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                contributed_on TEXT NOT NULL,
                FOREIGN KEY(goal_id) REFERENCES savings_goals(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS investment_positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                asset_class TEXT NOT NULL,
                account_label TEXT NOT NULL,
                market_value REAL NOT NULL,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, account_label)
            );

            CREATE TABLE IF NOT EXISTS tax_settings (
                id INTEGER PRIMARY KEY CHECK(id = 1),
                marginal_tax_rate REAL NOT NULL,
                annual_tax_budget REAL NOT NULL,
                monthly_withholding REAL NOT NULL,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        self._connection.execute(
            """
            INSERT INTO alert_settings (id, minimum_amount, sensitivity_factor, min_samples)
            VALUES (1, 100.0, 2.0, 3)
            ON CONFLICT(id) DO NOTHING
            """
        )
        self._connection.execute(
            """
            INSERT INTO tax_settings (id, marginal_tax_rate, annual_tax_budget, monthly_withholding)
            VALUES (1, 0.22, 5000.0, 300.0)
            ON CONFLICT(id) DO NOTHING
            """
        )
        self._connection.commit()
