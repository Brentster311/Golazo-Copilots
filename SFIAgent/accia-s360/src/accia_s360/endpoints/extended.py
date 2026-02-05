"""
Extended S360 API endpoints discovered from HAR analysis.
"""

import logging
from typing import Any

import requests

from accia_s360.config import S360Config
from accia_s360.exceptions import S360ApiError, S360AuthError
from accia_s360.models import SaveResult

logger = logging.getLogger(__name__)

__all__ = ["ExtendedEndpoints"]


class ExtendedEndpoints:
    """Extended S360 API endpoints discovered from HAR file analysis."""

    def __init__(
        self,
        config: S360Config,
        get_token_func: callable,
    ) -> None:
        self.config = config
        self._get_token = get_token_func

    def _get_headers(self) -> dict[str, str]:
        """Get request headers with authorization."""
        token = self._get_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
    ) -> dict[str, Any] | list | None:
        """Make an HTTP request and return JSON response."""
        url = f"{self.config.base_url}{endpoint}"
        headers = self._get_headers()

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json_data,
                timeout=self.config.timeout_seconds,
            )

            if response.status_code == 401:
                raise S360AuthError("Authentication expired")
            if response.status_code == 403:
                raise S360AuthError("Access forbidden")
            if response.status_code >= 400:
                raise S360ApiError(
                    f"API error: {response.text}",
                    endpoint=endpoint,
                    status_code=response.status_code,
                )

            if not response.text:
                return None
            return response.json()

        except requests.RequestException as e:
            raise S360ApiError(f"Request failed: {str(e)}", endpoint=endpoint) from e

    # ========== Action Items Endpoints ==========

    def get_action_owner_history(
        self,
        kpi_id: str,
        action_item_id: str,
    ) -> list[dict[str, Any]]:
        """
        Get action owner history for an action item.

        Args:
            kpi_id: The KPI ID.
            action_item_id: The action item ID.

        Returns:
            List of owner history records.
        """
        logger.info("Getting action owner history for: %s", action_item_id)
        return self._make_request(
            "GET",
            "/ActionItems/GetActionOwnerHistoryById",
            params={"KpiId": kpi_id, "id": action_item_id},
        ) or []

    def save_action_owners(
        self,
        kpi_id: str,
        action_owner_alias: str,
        action_owner_name: str,
        action_items: list[dict[str, str]],
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

        Example action_items:
            [{"ServiceId": "...", "ActionItemId": "...", "SLAType": "InSla"}]
        """
        logger.info("Saving action owners for %d items", len(action_items))
        payload = {
            "ActionOwnerAlias": action_owner_alias,
            "ActionOwnerName": action_owner_name,
            "KpiId": kpi_id,
            "ActionItems": action_items,
        }
        result = self._make_request("POST", "/ActionItems/SaveActionOwnersByIds", json_data=payload)
        return result is not None

    def get_customized_grid(
        self,
        kpi_id: str,
        audience: list[str],
        domain_id: str | None = None,
        program_ids: list[str] | None = None,
        sla_type_filter: int = 2,
        filters: list[dict[str, str]] | None = None,
        assigned_to: str = "",
        columns: list[str] | None = None,
    ) -> dict[str, Any]:
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
        logger.info("Getting customized grid for KPI: %s", kpi_id)
        payload = {
            "ActionItemId": kpi_id,
            "Audience": audience,
            "SlaTypeFilter": sla_type_filter,
            "RelationToAssignedTo": "",
            "AssignedTo": assigned_to,
            "DomainId": domain_id or "",
            "Filters": filters or [],
            "Columns": columns or [],
            "StartDueDate": "",
            "EndDueDate": "",
            "period": "",
            "ProgramIds": program_ids or [],
        }
        return self._make_request("POST", "/ActionItems/GetCustomizedGrid", json_data=payload) or {}

    def query_grid_filters(
        self,
        kpi_id: str,
        audience: list[str],
        domain_id: str | None = None,
        program_ids: list[str] | None = None,
        sla_type_filter: int = 2,
        filters: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        """
        Query available grid filter options.

        Args:
            kpi_id: The KPI/Action Item ID.
            audience: List of service/team IDs.
            domain_id: Domain ID.
            program_ids: Program IDs.
            sla_type_filter: SLA filter type.
            filters: Current filters.

        Returns:
            Available filter options.
        """
        logger.info("Querying grid filters for KPI: %s", kpi_id)
        payload = {
            "ActionItemId": kpi_id,
            "Audience": audience,
            "SlaTypeFilter": sla_type_filter,
            "RelationToAssignedTo": "",
            "AssignedTo": "",
            "DomainId": domain_id or "",
            "Filters": filters or [],
            "StartDueDate": "",
            "EndDueDate": "",
            "ProgramIds": program_ids or [],
        }
        return self._make_request("POST", "/ActionItems/QueryGridFilters", json_data=payload) or {}

    # ========== Common Components Endpoints ==========

    def search(self, search_text: str) -> list[dict[str, Any]]:
        """
        Search for users, services, or other entities.

        Args:
            search_text: Text to search for.

        Returns:
            List of search results with Id, Name, Group, Owners, Managers.
        """
        logger.info("Searching for: %s", search_text)
        result = self._make_request(
            "GET",
            "/CommonComponents/GetSearchData",
            params={"searchText": search_text},
        )
        return result.get("SearchDataList", []) if result else []

    # ========== KPIs Endpoints ==========

    def query_kpi_costs(
        self,
        kpi_ids: list[str],
        view_by_type: int = 0,
    ) -> dict[str, Any]:
        """
        Query cost information for KPIs.

        Args:
            kpi_ids: List of KPI IDs.
            view_by_type: View type (0=default).

        Returns:
            Cost data for the KPIs.
        """
        logger.info("Querying costs for %d KPIs", len(kpi_ids))
        payload = {
            "RequestObjects": kpi_ids,
            "ViewByType": view_by_type,
        }
        return self._make_request("POST", "/Kpis/Costing/QueryCostOfKpis", json_data=payload) or {}

    def query_metadata_fields(
        self,
        kpi_type: str = "ActionItem",
        metadata_fields: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Query KPI metadata fields.

        Args:
            kpi_type: Type of KPI (e.g., "ActionItem").
            metadata_fields: List of fields to query (e.g., ["ProgramsAssociation"]).

        Returns:
            Metadata field values.
        """
        logger.info("Querying metadata fields for type: %s", kpi_type)
        # Note: This uses v2 API
        url = f"{self.config.base_url.replace('/v1', '/v2')}/Kpis/Metadata/QueryFields"
        headers = self._get_headers()
        payload = {"MetadataFields": metadata_fields or ["ProgramsAssociation"]}

        try:
            response = requests.post(
                url,
                headers=headers,
                params={"kpiType": kpi_type},
                json=payload,
                timeout=self.config.timeout_seconds,
            )
            if response.status_code == 200:
                return response.json()
            return {}
        except requests.RequestException:
            return {}

    # ========== ADO (Azure DevOps) Endpoints ==========

    def get_ado_work_item_metadata(
        self,
        kpi_id: str,
        target_id: str,
        page_size: int = 10000,
    ) -> dict[str, Any]:
        """
        Get Azure DevOps work item metadata.

        Args:
            kpi_id: The KPI ID.
            target_id: The target/service ID.
            page_size: Number of items per page.

        Returns:
            ADO work item metadata.
        """
        logger.info("Getting ADO metadata for KPI: %s", kpi_id)
        return self._make_request(
            "GET",
            "/ADO/ADOWorkItemMetadata",
            params={"kpiId": kpi_id, "targetId": target_id, "pageSize": page_size},
        ) or {}

    # ========== Code Transformations Endpoints ==========

    def get_code_transformation_scenarios(
        self,
        kpi_ids: list[str],
        page_number: int = 1,
        page_size: int = 100,
        is_breeze_enabled: bool = True,
        use_cache: bool = False,
    ) -> dict[str, Any]:
        """
        Get code transformation scenarios.

        Args:
            kpi_ids: List of KPI IDs.
            page_number: Page number.
            page_size: Items per page.
            is_breeze_enabled: Whether Breeze is enabled.
            use_cache: Whether to use cache.

        Returns:
            Code transformation scenarios.
        """
        logger.info("Getting code transformation scenarios")
        params = {
            "kpiIds": ",".join(kpi_ids),
            "pageNumber": page_number,
            "pageSize": page_size,
            "isBreezeEnabled": str(is_breeze_enabled).lower(),
            "useCache": str(use_cache).lower(),
        }
        return self._make_request("GET", "/CodeTransformations/Scenarios", params=params) or {}

    def query_code_transformations(
        self,
        service_ids: list[str] | None = None,
        kpi_ids: list[str] | None = None,
        kpi_action_item_ids: list[str] | None = None,
        scenario_ids: list[str] | None = None,
        relationship_types: list[str] | None = None,
        page_number: int = 1,
        page_size: int = 500,
    ) -> dict[str, Any]:
        """
        Query code transformations.

        Args:
            service_ids: Filter by service IDs.
            kpi_ids: Filter by KPI IDs.
            kpi_action_item_ids: Filter by action item IDs.
            scenario_ids: Filter by scenario IDs.
            relationship_types: Types like "serviceKpiActionItem".
            page_number: Page number.
            page_size: Items per page.

        Returns:
            Code transformation data.
        """
        logger.info("Querying code transformations")
        payload = {
            "relationshipTypes": relationship_types or ["serviceKpiActionItem"],
            "scenarioIds": scenario_ids or [],
            "serviceIds": service_ids or [],
            "kpiIds": kpi_ids or [],
            "kpiSubtypes": [],
            "kpiActionItemIds": kpi_action_item_ids or [],
            "pageNumber": page_number,
            "pageSize": page_size,
        }
        return self._make_request(
            "POST",
            "/CodeTransformations/QueryCodeTransformations",
            json_data=payload,
        ) or {}

    # ========== Common Components - Additional Endpoints ==========

    def get_notification_alerts(
        self,
        alert_type: str = "AppAnnouncementType",
        row_count: int = 6,
    ) -> list[dict[str, Any]]:
        """
        Get notification alerts.

        Args:
            alert_type: Type of alerts to retrieve.
            row_count: Number of alerts to return.

        Returns:
            List of notification alerts.
        """
        logger.info("Getting notification alerts")
        payload = {"Type": alert_type, "RowCount": str(row_count)}
        return self._make_request("POST", "/CommonComponents/GetNotificationAlerts", json_data=payload) or []

    def get_forums(self) -> list[dict[str, Any]]:
        """
        Get all forums.

        Returns:
            List of forums.
        """
        logger.info("Getting forums")
        return self._make_request("GET", "/CommonComponents/GetForums") or []

    def get_domains(self) -> list[dict[str, Any]]:
        """
        Get all domains.

        Returns:
            List of domains.
        """
        logger.info("Getting domains")
        return self._make_request("GET", "/CommonComponents/GetDomains") or []

    def get_programs(self, program_id: str | None = None) -> dict[str, Any]:
        """
        Get all programs or a specific program's details.

        Uses the v2/Programs API to get program metadata including:
        - Objectives (SFI pillars like SFI-AR, SFI-ES, SFI-ID, SFI-NS, SFI-PS, SFI-TI)
        - KPIs associated with each program
        - Waves and their dates

        Args:
            program_id: Optional program ID. If provided, gets details for that program.
                       If None, returns all programs.

        Returns:
            Dict with Programs list (when no program_id) or single program details.
            Each program contains: Objectives, Kpis, ProgramId, DisplayName, etc.
        """
        # Use v2 API
        v2_base = self.config.base_url.replace('/v1', '/v2')
        headers = self._get_headers()

        if program_id:
            logger.info("Getting program details for: %s", program_id)
            url = f"{v2_base}/Programs/{program_id}"
        else:
            logger.info("Getting all programs")
            url = f"{v2_base}/Programs"

        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=self.config.timeout_seconds,
            )
            if response.status_code == 200:
                return response.json()
            if response.status_code >= 400:
                raise S360ApiError(
                    f"API error: {response.text}",
                    endpoint="/v2/Programs",
                    status_code=response.status_code,
                )
            return {}
        except requests.RequestException as e:
            raise S360ApiError(f"Request failed: {str(e)}", endpoint="/v2/Programs") from e

    def get_action_items_per_policy(
        self,
        service_ids: list[str] | None = None,
        kpi_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Get action items per policy.

        Args:
            service_ids: Filter by service IDs.
            kpi_ids: Filter by KPI IDs.

        Returns:
            Action items per policy data.
        """
        logger.info("Getting action items per policy")
        payload = {}
        if service_ids:
            payload["serviceId"] = service_ids
        if kpi_ids:
            payload["kpiId"] = kpi_ids
        return self._make_request("POST", "/CommonComponents/GetAllActionItemPerPolicy", json_data=payload) or {}

    def get_user_search_groups(self, user_alias: str) -> list[dict[str, Any]]:
        """
        Get search groups for a user.

        Args:
            user_alias: User's alias.

        Returns:
            List of search groups.
        """
        logger.info("Getting search groups for: %s", user_alias)
        return self._make_request(
            "GET",
            "/CommonComponents/graph/GetAllSearchGroups",
            params={"userAlias": user_alias},
        ) or []

    def get_default_landing_view(self, user_alias: str) -> dict[str, Any]:
        """
        Get default landing view for a user.

        Args:
            user_alias: User's alias.

        Returns:
            Default landing view configuration.
        """
        logger.info("Getting default landing view for: %s", user_alias)
        return self._make_request(
            "GET",
            "/CommonComponents/DefaultLandingView",
            params={"userAlias": user_alias},
        ) or {}

    def get_all_action_item_metadata(self) -> list[dict[str, Any]]:
        """
        Get all action item metadata.

        Returns:
            List of action item metadata.
        """
        logger.info("Getting all action item metadata")
        return self._make_request("GET", "/CommonComponents/GetAllActionItemMetadata") or []

    def query_people_hierarchy(self, audience: list[str]) -> dict[str, Any]:
        """
        Query people hierarchy nodes.

        Args:
            audience: List of user aliases or IDs.

        Returns:
            People hierarchy data.
        """
        logger.info("Querying people hierarchy")
        payload = {"Audience": audience}
        return self._make_request("POST", "/CommonComponents/QueryPeopleHierarchyNodes", json_data=payload) or {}

    # ========== Feature Flags Endpoints ==========

    def get_kpi_feature_flags(self) -> dict[str, Any]:
        """
        Get KPI feature flags.

        Returns:
            Feature flags configuration.
        """
        logger.info("Getting KPI feature flags")
        return self._make_request("GET", "/FeatureFlags/Kpis") or {}

    def query_feature_flags(self, audience: list[str]) -> dict[str, Any]:
        """
        Query feature flags for audience.

        Args:
            audience: List of service/team IDs.

        Returns:
            Feature flags for the audience.
        """
        logger.info("Querying feature flags")
        payload = {"Audience": audience}
        return self._make_request("POST", "/FeatureFlags/QueryFeatureFlags", json_data=payload) or {}

    # ========== Lifecycle Endpoints ==========

    def get_product_launch_summary(self) -> dict[str, Any]:
        """
        Get product launch summary.

        Returns:
            Product launch summary data.
        """
        logger.info("Getting product launch summary")
        return self._make_request("GET", "/Lifecycle/ProductLaunchSummary") or {}

    # ========== Data Factory Endpoints ==========

    def get_quarantined_jobs(self) -> list[dict[str, Any]]:
        """
        Get quarantined data factory jobs.

        Returns:
            List of quarantined jobs.
        """
        logger.info("Getting quarantined jobs")
        # Note: Uses v2 API
        url = f"{self.config.base_url.replace('/v1', '/v2')}/DataFactory/GetQuarantinedJobs"
        headers = self._get_headers()
        try:
            response = requests.get(url, headers=headers, timeout=self.config.timeout_seconds)
            if response.status_code == 200:
                return response.json()
            return []
        except requests.RequestException:
            return []

    # ========== Reliability KPI Endpoints ==========

    def get_reliability_metadata(self) -> dict[str, Any]:
        """
        Get reliability KPI metadata.

        Returns:
            Reliability metadata.
        """
        logger.info("Getting reliability metadata")
        return self._make_request("POST", "/ReliabilityKPI/GetReliabilityMetadata", json_data={}) or {}

    def get_reliability_kpi_values(
        self,
        audience: list[str],
        domain_id: str = "Reliability",
        forum_id: str = "",
        breakdown_by_service: bool = False,
        kpi_id: str = "All",
    ) -> dict[str, Any]:
        """
        Get reliability KPI values.

        Args:
            audience: List of service/team IDs.
            domain_id: Domain ID (default: "Reliability").
            forum_id: Forum ID filter.
            breakdown_by_service: Whether to break down by service.
            kpi_id: Specific KPI ID or "All".

        Returns:
            Reliability KPI values.
        """
        logger.info("Getting reliability KPI values")
        payload = {
            "audience": audience,
            "domainId": domain_id,
            "forumId": forum_id,
            "breakdownByService": breakdown_by_service,
            "kpiId": kpi_id,
        }
        return self._make_request("POST", "/ReliabilityKPI/GetReliabilityKPIValues", json_data=payload) or {}

    # ========== Action Items V2 Endpoints ==========

    def get_action_items_summary(
        self,
        audience: list[str],
        domain_id: str = "",
        assigned_to: str = "",
        relation_to_assigned_to: str = "",
        start_due_date: str = "",
        end_due_date: str = "",
    ) -> dict[str, Any]:
        """
        Get action items summary (v2 API).

        Args:
            audience: List of service/team IDs.
            domain_id: Domain ID filter.
            assigned_to: Filter by assigned user.
            relation_to_assigned_to: Relation filter.
            start_due_date: Start due date filter.
            end_due_date: End due date filter.

        Returns:
            Action items summary.
        """
        logger.info("Getting action items summary")
        payload = {
            "audience": audience,
            "relationToAssignedTo": relation_to_assigned_to,
            "assignedTo": assigned_to,
            "domainId": domain_id,
            "startDueDate": start_due_date,
            "endDueDate": end_due_date,
        }
        # Note: Uses v2 API
        url = f"{self.config.base_url.replace('/v1', '/v2')}/ActionItems/ActionItemsSummary"
        headers = self._get_headers()
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=self.config.timeout_seconds)
            if response.status_code == 200:
                return response.json()
            return {}
        except requests.RequestException:
            return {}

    def get_eta_and_annotation_data(
        self,
        audience: list[str],
        accessing_user_alias: str,
        eta_type: int = 1,
        assigned_to: str = "",
        sla_type_filter: str = "",
        show_missing: bool = False,
    ) -> dict[str, Any]:
        """
        Get ETA and annotation data (v2 API).

        Args:
            audience: List of service/team IDs.
            accessing_user_alias: Current user's alias.
            eta_type: ETA type filter.
            assigned_to: Filter by assigned user.
            sla_type_filter: SLA type filter.
            show_missing: Show missing ETAs and annotations.

        Returns:
            ETA and annotation data.
        """
        logger.info("Getting ETA and annotation data")
        payload = {
            "accessingUserAlias": accessing_user_alias,
            "audience": audience,
            "etaType": eta_type,
            "relationToAssignedTo": "",
            "assignedTo": assigned_to,
            "slaTypeFilter": sla_type_filter,
            "showMissingEtaAndAnnotations": show_missing,
            "startDueDate": "",
            "endDueDate": "",
        }
        url = f"{self.config.base_url.replace('/v1', '/v2')}/ActionItems/ETAAndAnnotationData"
        headers = self._get_headers()
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=self.config.timeout_seconds)
            if response.status_code == 200:
                return response.json()
            return {}
        except requests.RequestException:
            return {}

    def get_launch_criteria_summary(self, audience: list[str]) -> dict[str, Any]:
        """
        Get launch criteria summary.

        Args:
            audience: List of service/team IDs.

        Returns:
            Launch criteria summary.
        """
        logger.info("Getting launch criteria summary")
        payload = {"audience": audience}
        return self._make_request("POST", "/ActionItems/GetLaunchCriteriaSummary", json_data=payload) or {}

    # ========== KPI Priority Endpoints ==========

    def get_sub_services_priority_metadata(
        self,
        audience: list[str],
        accessing_user_alias: str,
        service_tree_node_type: int = 5,
    ) -> dict[str, Any]:
        """
        Get sub-services priority metadata.

        Args:
            audience: List of service/team IDs.
            accessing_user_alias: Current user's alias.
            service_tree_node_type: Service tree node type.

        Returns:
            Priority metadata.
        """
        logger.info("Getting sub-services priority metadata")
        payload = {
            "Audience": audience,
            "serviceTreeNodeType": service_tree_node_type,
            "accessingUserAlias": accessing_user_alias,
        }
        return self._make_request("POST", "/KpiPriority/GetSubServicesPriorityMetaData", json_data=payload) or {}

    def query_audience_type(self, audience_ids: list[str]) -> dict[str, Any]:
        """
        Query audience type.

        Args:
            audience_ids: List of audience IDs.

        Returns:
            Audience type information.
        """
        logger.info("Querying audience type")
        payload = {"AudienceIds": audience_ids}
        return self._make_request("POST", "/KpiPriority/QueryAudienceType", json_data=payload) or {}

    # ========== Costing Notification Endpoints ==========

    def query_costing_notification_eligibility(
        self,
        target_ids: list[str],
        user_alias: str = "",
        duration_part: int = 0,
        duration_magnitude: int = 7,
    ) -> dict[str, Any]:
        """
        Query costing notification eligibility.

        Args:
            target_ids: List of target/service IDs.
            user_alias: User alias filter.
            duration_part: Duration part.
            duration_magnitude: Duration magnitude.

        Returns:
            Eligibility data.
        """
        logger.info("Querying costing notification eligibility")
        payload = {
            "DurationPart": duration_part,
            "DurationMagnitude": duration_magnitude,
            "TargetIds": target_ids,
            "UserAlias": user_alias,
        }
        return self._make_request("POST", "/Kpis/Costing/User/Notification/QueryEligibility", json_data=payload) or {}

    # ========== Additional Endpoints from HAR3 ==========

    def get_details_summary(
        self,
        audience: list[str],
        domain_id: str = "",
        sla_type_filter: int = 3,
        action_item_id: str = "",
        forum_name: str = "",
        relation_to_assigned_to: str = "",
        assigned_to: str = "",
        filters: list[dict] | None = None,
    ) -> dict[str, Any]:
        """
        Get action items details summary.

        Args:
            audience: List of service/team IDs.
            domain_id: Domain ID filter.
            sla_type_filter: SLA filter (0=All, 1=InSla, 2=OutOfSla, 3=All).
            action_item_id: Specific KPI/action item ID.
            forum_name: Forum name filter.
            relation_to_assigned_to: Relation filter.
            assigned_to: Filter by assigned user.
            filters: Additional filters.

        Returns:
            Details summary data.
        """
        logger.info("Getting details summary")
        payload = {
            "Audience": audience,
            "SlaTypeFilter": sla_type_filter,
            "KpiRanking": "",
            "ActionItemId": action_item_id,
            "ForumName": forum_name,
            "RelationToAssignedTo": relation_to_assigned_to,
            "AssignedTo": assigned_to,
            "DomainId": domain_id,
            "Filters": filters or [],
            "StartDueDate": "",
            "EndDueDate": "",
        }
        return self._make_request("POST", "/ActionItems/GetDetailsSummary", json_data=payload) or {}

    def get_delegation_settings(self, user_alias: str) -> dict[str, Any]:
        """
        Get delegation settings for a user.

        Args:
            user_alias: User's alias.

        Returns:
            Delegation settings.
        """
        logger.info("Getting delegation settings for: %s", user_alias)
        return self._make_request(
            "GET",
            "/Delegation/GetDelegationSettings",
            params={"userAlias": user_alias},
        ) or {}

    def get_kpi_security(self, kpi_id: str) -> dict[str, Any]:
        """
        Get KPI security/onboarding settings.

        Args:
            kpi_id: The KPI ID.

        Returns:
            KPI security configuration.
        """
        logger.info("Getting KPI security for: %s", kpi_id)
        return self._make_request(
            "GET",
            "/Onboarding/GetKpiSecurity",
            params={"kpiId": kpi_id},
        ) or {}

    def get_is_resolution_self_attested(self, kpi_id: str, action_item_id: str) -> dict[str, Any]:
        """
        Check if resolution is self-attested.

        Args:
            kpi_id: The KPI ID.
            action_item_id: The action item ID.

        Returns:
            Self-attestation status.
        """
        logger.info("Checking self-attestation for: %s", action_item_id)
        return self._make_request(
            "GET",
            "/Attestations/GetIsResolutionSelfAttested",
            params={"kpiId": kpi_id, "actionItemId": action_item_id},
        ) or {}

    def get_kpi_target_type(self, kpi_id: str) -> dict[str, Any]:
        """
        Get KPI target type (v2 API).

        Args:
            kpi_id: The KPI ID.

        Returns:
            KPI target type information.
        """
        logger.info("Getting KPI target type for: %s", kpi_id)
        url = f"{self.config.base_url.replace('/v1', '/v2')}/Kpis/{kpi_id}/TargetType"
        headers = self._get_headers()
        try:
            response = requests.get(url, headers=headers, timeout=self.config.timeout_seconds)
            if response.status_code == 200:
                return response.json()
            return {}
        except requests.RequestException:
            return {}

    def get_kpi_metadata_v2(self, kpi_id: str) -> dict[str, Any]:
        """
        Get KPI metadata (v2 API).

        Args:
            kpi_id: The KPI ID.

        Returns:
            KPI metadata.
        """
        logger.info("Getting KPI metadata (v2) for: %s", kpi_id)
        url = f"{self.config.base_url.replace('/v1', '/v2')}/Kpis/{kpi_id}/Metadata"
        headers = self._get_headers()
        try:
            response = requests.get(url, headers=headers, timeout=self.config.timeout_seconds)
            if response.status_code == 200:
                return response.json()
            return {}
        except requests.RequestException:
            return {}

    def get_all_kpis_metadata(self) -> list[dict[str, Any]]:
        """
        Get metadata for all KPIs (v2 API).

        Returns:
            List of KPI metadata.
        """
        logger.info("Getting all KPIs metadata (v2)")
        url = f"{self.config.base_url.replace('/v1', '/v2')}/Kpis/Metadata"
        headers = self._get_headers()
        try:
            response = requests.get(url, headers=headers, timeout=self.config.timeout_seconds)
            if response.status_code == 200:
                return response.json()
            return []
        except requests.RequestException:
            return []

    def query_kpi_metadata_fields(self, fields: list[str]) -> dict[str, Any]:
        """
        Query specific KPI metadata fields (v2 API).

        Args:
            fields: List of metadata fields to query (e.g., ["ProgramsAssociation"]).

        Returns:
            Metadata fields data.
        """
        logger.info("Querying KPI metadata fields: %s", fields)
        url = f"{self.config.base_url.replace('/v1', '/v2')}/Kpis/Metadata/QueryFields"
        headers = self._get_headers()
        payload = {"MetadataFields": fields}
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=self.config.timeout_seconds)
            if response.status_code == 200:
                return response.json()
            return {}
        except requests.RequestException:
            return {}

    def get_all_kpi_action_item_type_metadata(self) -> list[dict[str, Any]]:
        """
        Get all KPI action item type metadata.

        Returns:
            List of action item type metadata.
        """
        logger.info("Getting all KPI action item type metadata")
        return self._make_request("GET", "/CommonComponents/GetAllKpiActionItemTypeMetadata") or []

    def get_code_transformation_scenarios(self) -> list[dict[str, Any]]:
        """
        Get code transformation scenarios.

        Returns:
            List of available scenarios.
        """
        logger.info("Getting code transformation scenarios")
        return self._make_request("GET", "/CodeTransformations/Scenarios") or []
