from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


class ConnectorError(RuntimeError):
    def __init__(self, category: str, actionable_message: str) -> None:
        super().__init__(actionable_message)
        self.category = category
        self.actionable_message = actionable_message


@dataclass(frozen=True, slots=True)
class TransactionRecord:
    provider_transaction_id: str
    posted_at: datetime
    amount: float
    merchant: str
    direction: str = "debit"


class FixtureConnector:
    """In-memory connector used for deterministic sync tests."""

    def __init__(self, institution: str) -> None:
        self.institution = institution
        self._records: dict[str, list[TransactionRecord]] = {}

    def set_transactions(self, access_token: str, transactions: list[TransactionRecord]) -> None:
        self._records[access_token] = list(transactions)

    def append_transaction(self, access_token: str, transaction: TransactionRecord) -> None:
        self._records.setdefault(access_token, []).append(transaction)

    def fetch_transactions(self, access_token: str, start_at: datetime) -> list[TransactionRecord]:
        self._raise_if_simulated_failure(access_token)
        records = self._records.get(access_token, [])
        return [record for record in records if record.posted_at >= start_at]

    @staticmethod
    def _raise_if_simulated_failure(access_token: str) -> None:
        if not access_token.startswith("fail:"):
            return

        reason = access_token.split(":", 1)[1].strip().lower()
        if reason == "connectivity":
            raise ConnectorError(
                "connectivity_error",
                "Could not reach institution endpoint. Check connectivity and retry sync.",
            )
        if reason == "auth":
            raise ConnectorError(
                "auth_error",
                "Institution authentication failed. Re-link account and retry sync.",
            )
        raise ConnectorError(
            "provider_error",
            "Provider returned an unexpected error. Please retry sync.",
        )
