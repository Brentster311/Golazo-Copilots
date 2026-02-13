"""Kusto (Azure Data Explorer) client for fetching incident descriptions.

Queries the IncidentDescriptions table in the IcmDataWarehouse database.
Uses accia-datacollection KustoHandler per TechBestPractices.
No Tkinter dependency — fully testable in isolation.
"""
from __future__ import annotations

import re

try:
    from azure.identity import AzureCliCredential, ManagedIdentityCredential
    from accia.datacollection import KustoHandler

    KUSTO_AVAILABLE = True
except ImportError:  # pragma: no cover
    KUSTO_AVAILABLE = False

_INCIDENT_ID_RE = re.compile(r"^[\w\-]+$")

_KQL_TEMPLATE = (
    "IncidentDescriptions"
    " | where IncidentId == '{incident_id}'"
    " | project Description"
    " | take 1"
)


class KustoClient:
    """Fetch incident descriptions from Azure Data Explorer."""

    def __init__(self, cluster: str, database: str) -> None:
        self._cluster = cluster
        self._database = database

    def _execute_query(self, query: str):
        """Execute a KQL query via accia.datacollection.KustoHandler.

        Returns a pandas DataFrame. Separated for easy mocking in tests.
        """
        handler = KustoHandler(
            AlternateAADCredentialsList=[
                AzureCliCredential(),
                ManagedIdentityCredential(),
            ],
            UseDefaultCredentials=False,
        )
        return handler.GetDataFrameFromKustoQuery(
            Cluster=self._cluster,
            Database=self._database,
            Query=query,
        )

    def fetch_incident(self, incident_id: str) -> str:
        """Fetch incident description text from Kusto.

        Args:
            incident_id: The incident identifier (e.g. "INC-12345").

        Returns:
            The incident description text.

        Raises:
            ValueError: If incident_id is empty or whitespace-only.
            RuntimeError: If the incident is not found or the query fails.
        """
        stripped = incident_id.strip()
        if not stripped:
            raise ValueError("Incident ID must not be empty.")

        # Sanitize: allow only word chars and hyphens
        if not _INCIDENT_ID_RE.match(stripped):
            raise ValueError(
                f"Incident ID contains invalid characters: {stripped!r}"
            )

        query = _KQL_TEMPLATE.format(incident_id=stripped)

        try:
            df = self._execute_query(query)
        except Exception as exc:
            raise RuntimeError(f"Kusto query failed: {exc}") from exc

        if df.empty:
            raise RuntimeError(
                f"Incident '{stripped}' not found in IncidentDescriptions."
            )

        return str(df.iloc[0, 0])
