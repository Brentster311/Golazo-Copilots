"""
Microsoft Graph API endpoint for people hierarchy.

Provides org tree traversal: manager chain upward, direct reports downward.
Uses MS Graph v1.0 /users endpoints.
"""

import logging
import time
from typing import Callable

import requests

from accia_s360.config import S360Config
from accia_s360.exceptions import S360ApiError, S360AuthError
from accia_s360.models import OrgPerson, OrgTree

logger = logging.getLogger(__name__)

__all__ = ["GraphEndpoint"]

GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"
_SELECT_FIELDS = "displayName,mailNickname,jobTitle,department,id"
_MAX_CHAIN_DEPTH = 10
_MAX_RETRIES = 3


class GraphEndpoint:
    """Microsoft Graph API endpoint for org hierarchy queries."""

    def __init__(
        self,
        config: S360Config,
        get_token_func: Callable[[], str],
    ) -> None:
        self.config = config
        self._get_token = get_token_func

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _headers(self) -> dict[str, str]:
        token = self._get_token()
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }

    def _graph_get(self, url: str) -> requests.Response:
        """GET with retry on 429, auth error detection, and network error wrapping.

        *url* must be a fully-qualified URL (including GRAPH_BASE_URL prefix).
        """
        last_exc: Exception | None = None
        for attempt in range(1 + _MAX_RETRIES):
            try:
                resp = requests.get(
                    url,
                    headers=self._headers(),
                    timeout=self.config.timeout_seconds,
                )
            except requests.RequestException as exc:
                raise S360ApiError(
                    f"Graph request failed: {exc}",
                    endpoint=url,
                ) from exc

            if resp.status_code == 429:
                if attempt >= _MAX_RETRIES:
                    raise S360ApiError(
                        "Graph rate limit exceeded after retries",
                        endpoint=url,
                        status_code=429,
                    )
                retry_after = int(resp.headers.get("Retry-After", str(2 ** attempt)))
                logger.warning(
                    "Graph 429 rate-limited (attempt %d/%d), retrying in %ds",
                    attempt + 1, _MAX_RETRIES, retry_after,
                )
                time.sleep(retry_after)
                continue

            if resp.status_code in (401, 403):
                raise S360AuthError(
                    f"Graph authentication/authorization failed (HTTP {resp.status_code})",
                    scope="https://graph.microsoft.com/.default",
                )

            return resp

        # Should not reach here, but just in case
        raise S360ApiError("Graph request failed after retries", endpoint=url)

    @staticmethod
    def _upn(alias: str) -> str:
        return f"{alias}@microsoft.com"

    def _user_url(self, alias: str, suffix: str = "") -> str:
        return f"{GRAPH_BASE_URL}/users/{self._upn(alias)}{suffix}?$select={_SELECT_FIELDS}"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_manager_chain(self, alias: str) -> list[OrgPerson]:
        """Walk the manager chain upward from *alias* to CEO.

        Returns an ordered list ``[immediate_manager, ..., CEO]``.
        An empty list means the target user has no manager (is CEO).

        Raises:
            S360ApiError: If the user does not exist or a Graph error occurs.
            S360AuthError: If authentication fails.
        """
        logger.info("Querying manager chain for %s", alias)
        chain: list[OrgPerson] = []
        seen_aliases: set[str] = set()
        current_alias = alias

        for _ in range(_MAX_CHAIN_DEPTH):
            url = self._user_url(current_alias, "/manager")
            resp = self._graph_get(url)

            if resp.status_code == 404:
                # Distinguish CEO (no manager) from user-not-found.
                if not chain:
                    # First call — could be CEO or non-existent user.
                    # Verify user exists.
                    verify_url = self._user_url(alias)
                    verify_resp = self._graph_get(verify_url)
                    if verify_resp.status_code == 404:
                        raise S360ApiError(
                            f"User '{alias}' not found in Graph",
                            endpoint=url,
                            status_code=404,
                        )
                    # User exists but has no manager → CEO
                break

            if resp.status_code >= 400:
                raise S360ApiError(
                    f"Graph error querying manager for {current_alias}: {resp.text}",
                    endpoint=url,
                    status_code=resp.status_code,
                )

            data = resp.json()
            person = OrgPerson.from_graph_response(data)

            # Cycle protection
            if person.alias in seen_aliases:
                logger.warning("Cycle detected in manager chain at %s", person.alias)
                break

            seen_aliases.add(person.alias)
            chain.append(person)
            current_alias = person.alias

        return chain

    def get_direct_reports(
        self,
        alias: str,
        *,
        exclude_sc_alts: bool = True,
    ) -> list[OrgPerson]:
        """Get direct reports for *alias*.

        Args:
            alias: Microsoft alias (e.g. ``"muralic"``).
            exclude_sc_alts: If True (default), filter out SC ALT accounts.

        Returns:
            List of ``OrgPerson`` for each direct report.

        Raises:
            S360ApiError: If the user does not exist or a Graph error occurs.
            S360AuthError: If authentication fails.
        """
        logger.info("Querying direct reports for %s", alias)
        url = self._user_url(alias, "/directReports")
        people: list[OrgPerson] = []

        while url:
            resp = self._graph_get(url)

            if resp.status_code == 404:
                raise S360ApiError(
                    f"User '{alias}' not found in Graph",
                    endpoint=url,
                    status_code=404,
                )

            if resp.status_code >= 400:
                raise S360ApiError(
                    f"Graph error querying direct reports for {alias}: {resp.text}",
                    endpoint=url,
                    status_code=resp.status_code,
                )

            data = resp.json()
            for item in data.get("value", []):
                person = OrgPerson.from_graph_response(item)
                if exclude_sc_alts and person.is_sc_alt():
                    logger.debug("Filtered SC ALT: %s", person.alias)
                    continue
                people.append(person)

            # Handle pagination
            url = data.get("@odata.nextLink")

        return people

    def get_org_tree(self, alias: str, *, depth: int = 2) -> OrgTree:
        """Build a nested org tree starting from *alias*.

        Args:
            alias: Microsoft alias (e.g. ``"muralic"``).
            depth: How many levels of reports to fetch (default 2).
                   ``depth=0`` returns only the target person.

        Returns:
            ``OrgTree`` with the target person and nested direct reports.

        Raises:
            S360ApiError: If the user does not exist or a Graph error occurs.
            S360AuthError: If authentication fails.
        """
        logger.info("Building org tree for %s (depth=%d)", alias, depth)
        # Fetch the target person's info
        url = self._user_url(alias)
        resp = self._graph_get(url)

        if resp.status_code == 404:
            raise S360ApiError(
                f"User '{alias}' not found in Graph",
                endpoint=url,
                status_code=404,
            )
        if resp.status_code >= 400:
            raise S360ApiError(
                f"Graph error fetching user {alias}: {resp.text}",
                endpoint=url,
                status_code=resp.status_code,
            )

        person = OrgPerson.from_graph_response(resp.json())
        return self._build_subtree(person, depth)

    def _build_subtree(self, person: OrgPerson, remaining_depth: int) -> OrgTree:
        """Recursively build an OrgTree node."""
        if remaining_depth <= 0:
            return OrgTree(person=person)

        reports = self.get_direct_reports(person.alias)
        children = [
            self._build_subtree(r, remaining_depth - 1)
            for r in reports
        ]
        return OrgTree(person=person, direct_reports=children)
