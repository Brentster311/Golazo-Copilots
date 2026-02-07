"""
Main S360 Client facade.
"""

import logging
from datetime import datetime

from accia_s360.auth import AuthManager
from accia_s360.cache import CacheManager
from accia_s360.config import S360Config
from accia_s360.endpoints.action_items import ActionItemsEndpoint
from accia_s360.endpoints.discovery import DiscoveryEndpoint
from accia_s360.endpoints.extended import ExtendedEndpoints
from accia_s360.models import (
    EndpointInfo,
    EtaHistoryItem,
    EtaUpdate,
    SaveResult,
    UserInfo,
)

logger = logging.getLogger(__name__)

__all__ = ["S360Client"]


class S360Client:
    """
    Main client for S360 API access.

    This is the primary entry point for all S360 operations.
    Handles authentication, caching, and API calls transparently.

    Usage:
        client = S360Client()
        user = client.get_current_user()
        history = client.get_eta_history(kpi_id, action_item_id)
    """

    def __init__(self, config: S360Config | None = None) -> None:
        """
        Initialize the S360 client.

        Args:
            config: Optional configuration. Uses defaults if not provided.
        """
        self.config = config or S360Config()
        self._auth = AuthManager(self.config)
        self._cache = CacheManager(self.config)
        self._action_items = ActionItemsEndpoint(self.config, self._auth.get_s360_token)
        self._discovery = DiscoveryEndpoint(self.config, self._auth.get_s360_token)
        self._extended = ExtendedEndpoints(self.config, self._auth.get_s360_token)

        # Configure logging
        logging.basicConfig(
            level=getattr(logging, self.config.log_level.upper(), logging.INFO),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

    def get_current_user(self, force_refresh: bool = False) -> UserInfo:
        """
        Get information about the currently authenticated user.

        Args:
            force_refresh: If True, bypass cache and fetch fresh data.

        Returns:
            UserInfo with the current user's details.

        Raises:
            S360AuthError: If authentication fails.
        """
        return self._auth.get_current_user(force_refresh=force_refresh)

    def get_eta_history(
        self,
        kpi_id: str,
        action_item_id: str,
        use_cache: bool = True,
    ) -> list[EtaHistoryItem]:
        """
        Get ETA history for an action item.

        Args:
            kpi_id: The KPI ID.
            action_item_id: The action item ID.
            use_cache: Whether to use cached data if available.

        Returns:
            List of ETA history items.

        Raises:
            S360ApiError: If the API call fails.
            S360AuthError: If authentication fails.
        """
        endpoint = "/ActionItems/GetEtaHistoryById"
        params = {"KpiId": kpi_id, "id": action_item_id}

        # Check cache
        if use_cache:
            cached = self._cache.get(endpoint, params)
            if cached is not None:
                logger.debug("Returning cached ETA history")
                return [EtaHistoryItem.from_api_response(item) for item in cached]

        # Fetch from API
        result = self._action_items.get_eta_history(kpi_id, action_item_id)

        # Cache the raw response
        if use_cache and result:
            raw_data = [
                {
                    "id": item.id,
                    "eta": item.eta.isoformat() if item.eta else None,
                    "status": item.status,
                    "notes": item.notes,
                    "createdAt": item.created_at.isoformat() if item.created_at else None,
                }
                for item in result
            ]
            self._cache.set(endpoint, raw_data, params)

        return result

    def save_etas(self, updates: list[EtaUpdate]) -> SaveResult:
        """
        Save ETA updates to S360.

        Args:
            updates: List of ETA updates to save.

        Returns:
            SaveResult indicating success/failure.

        Raises:
            S360ApiError: If the API call fails.
            S360AuthError: If authentication fails.
        """
        result = self._action_items.save_etas(updates)

        # Invalidate cache for affected action items
        if result.success:
            for update in updates:
                self._cache.invalidate(
                    "/ActionItems/GetEtaHistoryById",
                    {"KpiId": update.kpi_id, "id": update.action_item_id},
                )

        return result

    def save_eta(
        self,
        kpi_id: str,
        service_id: str,
        action_item_id: str,
        new_eta: datetime,
        notes: str,
        assigned_to: str = "",
        sla_type: str = "InSla",
    ) -> SaveResult:
        """
        Convenience method to save a single ETA update.

        Args:
            kpi_id: The KPI ID.
            service_id: The service ID.
            action_item_id: The action item ID.
            new_eta: The new ETA datetime.
            notes: Status notes.
            assigned_to: Alias of the action owner.
            sla_type: SLA type (default: "InSla").

        Returns:
            SaveResult indicating success/failure.
        """
        update = EtaUpdate(
            kpi_id=kpi_id,
            service_id=service_id,
            action_item_id=action_item_id,
            new_eta=new_eta,
            notes=notes,
            assigned_to=assigned_to,
            sla_type=sla_type,
        )
        return self.save_etas([update])

    def discover_endpoints(
        self,
        probe_common: bool = True,
    ) -> list[EndpointInfo]:
        """
        Discover available S360 API endpoints.

        Args:
            probe_common: If True, probe common REST patterns.

        Returns:
            List of discovered endpoints.
        """
        return self._discovery.discover_endpoints(probe_common=probe_common)

    def get_swagger_spec(self) -> dict | None:
        """
        Try to retrieve OpenAPI/Swagger specification.

        Returns:
            The spec dict if found, None otherwise.
        """
        return self._discovery.get_swagger_spec()

    def clear_cache(self) -> int:
        """
        Clear all cached data.

        Returns:
            Number of cache entries cleared.
        """
        return self._cache.clear()

    def test_connection(self) -> dict[str, bool | str]:
        """
        Test the connection to S360 APIs.

        Returns:
            Dict with connection test results.
        """
        results: dict[str, bool | str] = {}

        # Test S360 auth
        try:
            self._auth.get_s360_token()
            results["s360_auth"] = True
        except Exception as e:
            results["s360_auth"] = False
            results["s360_auth_error"] = str(e)

        # Test Graph auth
        try:
            self._auth.get_graph_token()
            results["graph_auth"] = True
        except Exception as e:
            results["graph_auth"] = False
            results["graph_auth_error"] = str(e)

        # Test user info
        try:
            user = self.get_current_user()
            results["user_info"] = True
            results["user_alias"] = user.alias
        except Exception as e:
            results["user_info"] = False
            results["user_info_error"] = str(e)

        return results

    # ========== Extended API Methods ==========

    def search(self, search_text: str) -> list[dict]:
        """
        Search for users, services, or other entities.

        Args:
            search_text: Text to search for.

        Returns:
            List of search results.
        """
        return self._extended.search(search_text)

    def get_action_owner_history(
        self,
        kpi_id: str,
        action_item_id: str,
    ) -> list[dict]:
        """
        Get action owner history for an action item.

        Args:
            kpi_id: The KPI ID.
            action_item_id: The action item ID.

        Returns:
            List of owner history records.
        """
        return self._extended.get_action_owner_history(kpi_id, action_item_id)

    def save_action_owners(
        self,
        kpi_id: str,
        action_owner_alias: str,
        action_owner_name: str,
        action_items: list[dict],
    ) -> bool:
        """
        Save action owners for action items.

        Args:
            kpi_id: The KPI ID.
            action_owner_alias: Owner's alias (e.g., "brentj").
            action_owner_name: Owner's full name.
            action_items: List of dicts with ServiceId, ActionItemId, SLAType.

        Returns:
            True if successful.
        """
        return self._extended.save_action_owners(
            kpi_id, action_owner_alias, action_owner_name, action_items
        )

    def get_action_items_grid(
        self,
        kpi_id: str,
        audience: list[str],
        domain_id: str | None = None,
        program_ids: list[str] | None = None,
        sla_type_filter: int = 2,
        filters: list[dict] | None = None,
        assigned_to: str = "",
        columns: list[str] | None = None,
    ) -> dict:
        """
        Get customized action items grid data.

        Args:
            kpi_id: The KPI/Action Item ID.
            audience: List of service/team IDs to filter by.
            domain_id: Domain ID for filtering.
            program_ids: List of program IDs.
            sla_type_filter: SLA filter (0=InSla, 1=ApproachingSla, 2=OutOfSla, 3=All).
            filters: Additional filters as Key/Value pairs.
            assigned_to: Filter by assigned user.
            columns: List of column names to include (e.g., ['S360_ProgramIds']).

        Returns:
            Grid data with Columns and Rows.
        """
        return self._extended.get_customized_grid(
            kpi_id, audience, domain_id, program_ids, sla_type_filter, filters, assigned_to, columns
        )

    def query_grid_filters(
        self,
        kpi_id: str,
        audience: list[str],
        domain_id: str | None = None,
        program_ids: list[str] | None = None,
    ) -> dict:
        """
        Query available grid filter options.

        Returns:
            Available filter options.
        """
        return self._extended.query_grid_filters(kpi_id, audience, domain_id, program_ids)

    def get_kpi_costs(self, kpi_ids: list[str]) -> dict:
        """
        Query cost information for KPIs.

        Args:
            kpi_ids: List of KPI IDs.

        Returns:
            Cost data for the KPIs.
        """
        return self._extended.query_kpi_costs(kpi_ids)

    def get_ado_metadata(
        self,
        kpi_id: str,
        target_id: str,
        page_size: int = 10000,
    ) -> dict:
        """
        Get Azure DevOps work item metadata.

        Args:
            kpi_id: The KPI ID.
            target_id: The target/service ID.
            page_size: Number of items per page.

        Returns:
            ADO work item metadata.
        """
        return self._extended.get_ado_work_item_metadata(kpi_id, target_id, page_size)

    def get_code_transformations(
        self,
        service_ids: list[str] | None = None,
        kpi_ids: list[str] | None = None,
        kpi_action_item_ids: list[str] | None = None,
    ) -> dict:
        """
        Query code transformations.

        Args:
            service_ids: Filter by service IDs.
            kpi_ids: Filter by KPI IDs.
            kpi_action_item_ids: Filter by action item IDs.

        Returns:
            Code transformation data.
        """
        return self._extended.query_code_transformations(
            service_ids=service_ids,
            kpi_ids=kpi_ids,
            kpi_action_item_ids=kpi_action_item_ids,
        )

    # ========== Common Components ==========

    def get_notification_alerts(
        self,
        alert_type: str = "AppAnnouncementType",
        row_count: int = 6,
    ) -> list[dict]:
        """
        Get notification alerts.

        Args:
            alert_type: Type of alerts.
            row_count: Number of alerts.

        Returns:
            List of notification alerts.
        """
        return self._extended.get_notification_alerts(alert_type, row_count)

    def get_forums(self) -> list[dict]:
        """Get all forums."""
        return self._extended.get_forums()

    def get_domains(self) -> list[dict]:
        """Get all domains."""
        return self._extended.get_domains()

    def get_programs(self, program_id: str | None = None) -> dict:
        """
        Get all programs or a specific program's details.

        Uses the v2/Programs API to get program metadata including objectives,
        KPIs, and wave information.

        Args:
            program_id: Optional program ID for single program details.

        Returns:
            Dict with Programs list or single program details.
        """
        return self._extended.get_programs(program_id)

    def get_action_items_per_policy(
        self,
        service_ids: list[str] | None = None,
        kpi_ids: list[str] | None = None,
    ) -> dict:
        """Get action items per policy."""
        return self._extended.get_action_items_per_policy(service_ids, kpi_ids)

    def get_user_search_groups(self, user_alias: str) -> list[dict]:
        """Get search groups for a user."""
        return self._extended.get_user_search_groups(user_alias)

    def get_default_landing_view(self, user_alias: str) -> dict:
        """Get default landing view for a user."""
        return self._extended.get_default_landing_view(user_alias)

    def get_all_action_item_metadata(self) -> list[dict]:
        """Get all action item metadata."""
        return self._extended.get_all_action_item_metadata()

    def query_people_hierarchy(self, audience: list[str]) -> dict:
        """Query people hierarchy nodes."""
        return self._extended.query_people_hierarchy(audience)

    # ========== Feature Flags ==========

    def get_kpi_feature_flags(self) -> dict:
        """Get KPI feature flags."""
        return self._extended.get_kpi_feature_flags()

    def query_feature_flags(self, audience: list[str]) -> dict:
        """Query feature flags for audience."""
        return self._extended.query_feature_flags(audience)

    # ========== Lifecycle ==========

    def get_product_launch_summary(self) -> dict:
        """Get product launch summary."""
        return self._extended.get_product_launch_summary()

    # ========== Data Factory ==========

    def get_quarantined_jobs(self) -> list[dict]:
        """Get quarantined data factory jobs."""
        return self._extended.get_quarantined_jobs()

    # ========== Reliability KPI ==========

    def get_reliability_metadata(self) -> dict:
        """Get reliability KPI metadata."""
        return self._extended.get_reliability_metadata()

    def get_reliability_kpi_values(
        self,
        audience: list[str],
        domain_id: str = "Reliability",
        breakdown_by_service: bool = False,
    ) -> dict:
        """Get reliability KPI values."""
        return self._extended.get_reliability_kpi_values(
            audience, domain_id, breakdown_by_service=breakdown_by_service
        )

    # ========== Action Items V2 ==========

    def get_action_items_summary(
        self,
        audience: list[str],
        domain_id: str = "",
        assigned_to: str = "",
    ) -> dict:
        """
        Get action items summary (v2 API).

        Args:
            audience: List of service/team IDs.
            domain_id: Domain ID filter.
            assigned_to: Filter by assigned user.

        Returns:
            Action items summary.
        """
        return self._extended.get_action_items_summary(
            audience, domain_id=domain_id, assigned_to=assigned_to
        )

    def get_eta_and_annotation_data(
        self,
        audience: list[str],
        accessing_user_alias: str = "",
        eta_type: int = 1,
    ) -> dict:
        """
        Get ETA and annotation data (v2 API).

        Args:
            audience: List of service/team IDs.
            accessing_user_alias: Current user's alias (auto-detected if empty).
            eta_type: ETA type filter.

        Returns:
            ETA and annotation data.
        """
        if not accessing_user_alias:
            user = self.get_current_user()
            accessing_user_alias = user.alias
        return self._extended.get_eta_and_annotation_data(
            audience, accessing_user_alias, eta_type
        )

    def get_launch_criteria_summary(self, audience: list[str]) -> dict:
        """Get launch criteria summary."""
        return self._extended.get_launch_criteria_summary(audience)

    # ========== KPI Priority ==========

    def get_sub_services_priority_metadata(
        self,
        audience: list[str],
        accessing_user_alias: str = "",
    ) -> dict:
        """Get sub-services priority metadata."""
        if not accessing_user_alias:
            user = self.get_current_user()
            accessing_user_alias = user.alias
        return self._extended.get_sub_services_priority_metadata(
            audience, accessing_user_alias
        )

    def query_audience_type(self, audience_ids: list[str]) -> dict:
        """Query audience type."""
        return self._extended.query_audience_type(audience_ids)

    # ========== Costing ==========

    def query_costing_notification_eligibility(
        self,
        target_ids: list[str],
        user_alias: str = "",
    ) -> dict:
        """Query costing notification eligibility."""
        return self._extended.query_costing_notification_eligibility(
            target_ids, user_alias
        )

    # ========== Additional Methods (HAR3) ==========

    def get_details_summary(
        self,
        audience: list[str],
        domain_id: str = "",
        sla_type_filter: int = 3,
        action_item_id: str = "",
    ) -> dict:
        """Get action items details summary."""
        return self._extended.get_details_summary(
            audience, domain_id=domain_id, sla_type_filter=sla_type_filter,
            action_item_id=action_item_id
        )

    def get_delegation_settings(self, user_alias: str = "") -> dict:
        """Get delegation settings for a user."""
        if not user_alias:
            user = self.get_current_user()
            user_alias = user.alias
        return self._extended.get_delegation_settings(user_alias)

    def get_kpi_security(self, kpi_id: str) -> dict:
        """Get KPI security/onboarding settings."""
        return self._extended.get_kpi_security(kpi_id)

    def get_is_resolution_self_attested(self, kpi_id: str, action_item_id: str) -> dict:
        """Check if resolution is self-attested."""
        return self._extended.get_is_resolution_self_attested(kpi_id, action_item_id)

    def get_kpi_target_type(self, kpi_id: str) -> dict:
        """Get KPI target type (v2 API)."""
        return self._extended.get_kpi_target_type(kpi_id)

    def get_kpi_metadata_v2(self, kpi_id: str) -> dict:
        """Get KPI metadata (v2 API)."""
        return self._extended.get_kpi_metadata_v2(kpi_id)

    def get_all_kpis_metadata(self) -> list[dict]:
        """Get metadata for all KPIs (v2 API)."""
        return self._extended.get_all_kpis_metadata()

    def query_kpi_metadata_fields(self, fields: list[str]) -> dict:
        """Query specific KPI metadata fields (v2 API)."""
        return self._extended.query_kpi_metadata_fields(fields)

    def get_all_kpi_action_item_type_metadata(self) -> list[dict]:
        """Get all KPI action item type metadata."""
        return self._extended.get_all_kpi_action_item_type_metadata()

    def get_code_transformation_scenarios(self) -> list[dict]:
        """Get code transformation scenarios."""
        return self._extended.get_code_transformation_scenarios()
