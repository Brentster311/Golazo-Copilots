from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Protocol


class ConnectorError(RuntimeError):
    def __init__(self, category: str, actionable_message: str) -> None:
        super().__init__(actionable_message)
        self.category = category
        self.actionable_message = actionable_message


class DirectConnectorConnectivityError(RuntimeError):
    """Raised when a direct provider request cannot reach the endpoint."""


class DirectConnectorAuthError(RuntimeError):
    """Raised when direct provider credentials or tokens are rejected."""


class DirectConnectorProviderError(RuntimeError):
    """Raised when provider payloads are invalid or provider state is unexpected."""


@dataclass(frozen=True, slots=True)
class TransactionRecord:
    provider_transaction_id: str
    posted_at: datetime
    amount: float
    merchant: str
    direction: str = "debit"


class ConnectorProtocol(Protocol):
    def fetch_transactions(self, access_token: str, start_at: datetime) -> list[TransactionRecord]:
        ...


class DirectProviderProtocol(Protocol):
    def authenticate(self, username: str, password: str) -> str:
        ...

    def fetch_transactions(self, access_token: str, start_at: datetime) -> list[TransactionRecord | dict[str, Any]]:
        ...


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


class DirectInstitutionConnector:
    """Connector that maps a provider adapter into normalized planner records."""

    def __init__(
        self,
        institution: str,
        provider: DirectProviderProtocol,
        *,
        mode: str = "test",
    ) -> None:
        self.institution = institution
        self._provider = provider
        self._mode = mode.strip().lower()

    def authenticate_account(self, username: str, password: str) -> str:
        self._ensure_non_test_mode()
        if not username.strip() or not password.strip():
            raise ConnectorError(
                "auth_error",
                "Institution authentication failed. Re-link account and retry sync.",
            )

        try:
            access_token = self._provider.authenticate(username=username, password=password)
        except Exception as error:  # pragma: no cover - exercised via mapped categories in tests
            raise self._to_connector_error(error) from error

        if not str(access_token).strip():
            raise ConnectorError(
                "auth_error",
                "Institution authentication failed. Re-link account and retry sync.",
            )
        return str(access_token)

    def fetch_transactions(self, access_token: str, start_at: datetime) -> list[TransactionRecord]:
        self._ensure_non_test_mode()
        if not access_token.strip():
            raise ConnectorError(
                "auth_error",
                "Institution authentication failed. Re-link account and retry sync.",
            )

        try:
            raw_records = self._provider.fetch_transactions(access_token=access_token, start_at=start_at)
        except Exception as error:
            raise self._to_connector_error(error) from error

        normalized = [self._to_transaction_record(raw) for raw in raw_records]
        return [record for record in normalized if record.posted_at >= start_at]

    def _ensure_non_test_mode(self) -> None:
        if self._mode == "test":
            raise ConnectorError(
                "provider_error",
                "Direct connector is disabled in test mode. Enable non-test mode and retry sync.",
            )

    @staticmethod
    def _to_connector_error(error: Exception) -> ConnectorError:
        if isinstance(error, ConnectorError):
            return error
        if isinstance(error, (DirectConnectorConnectivityError, TimeoutError, ConnectionError, OSError)):
            return ConnectorError(
                "connectivity_error",
                "Could not reach institution endpoint. Check connectivity and retry sync.",
            )
        if isinstance(error, (DirectConnectorAuthError, PermissionError)):
            return ConnectorError(
                "auth_error",
                "Institution authentication failed. Re-link account and retry sync.",
            )
        return ConnectorError(
            "provider_error",
            "Provider returned an unexpected error. Please retry sync.",
        )

    @staticmethod
    def _to_transaction_record(raw: TransactionRecord | dict[str, Any]) -> TransactionRecord:
        if isinstance(raw, TransactionRecord):
            return raw

        if not isinstance(raw, dict):
            raise DirectConnectorProviderError("provider record must be a mapping or TransactionRecord")

        provider_id = str(raw.get("provider_transaction_id") or raw.get("id") or "").strip()
        merchant = str(raw.get("merchant") or "").strip()
        direction = str(raw.get("direction") or "debit").strip().lower() or "debit"

        if not provider_id:
            raise DirectConnectorProviderError("provider record missing provider_transaction_id")
        if not merchant:
            raise DirectConnectorProviderError("provider record missing merchant")

        posted_at_raw = raw.get("posted_at")
        if isinstance(posted_at_raw, datetime):
            posted_at = posted_at_raw
        elif isinstance(posted_at_raw, str):
            normalized_iso = posted_at_raw.replace("Z", "+00:00")
            posted_at = datetime.fromisoformat(normalized_iso)
        else:
            raise DirectConnectorProviderError("provider record missing posted_at")

        if posted_at.tzinfo is None:
            posted_at = posted_at.replace(tzinfo=UTC)

        try:
            amount = float(raw.get("amount"))
        except (TypeError, ValueError) as error:
            raise DirectConnectorProviderError("provider record contains invalid amount") from error

        return TransactionRecord(
            provider_transaction_id=provider_id,
            posted_at=posted_at,
            amount=amount,
            merchant=merchant,
            direction=direction,
        )


class FirstTechDirectConnector(DirectInstitutionConnector):
    def __init__(self, provider: DirectProviderProtocol, *, mode: str = "test") -> None:
        super().__init__("First Tech Federal Credit Union", provider, mode=mode)


class FidelityDirectConnector(DirectInstitutionConnector):
    def __init__(self, provider: DirectProviderProtocol, *, mode: str = "test") -> None:
        super().__init__("Fidelity", provider, mode=mode)
