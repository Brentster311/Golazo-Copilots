"""
Unit tests for GraphEndpoint — MS Graph people hierarchy.

Tests T01–T34 from SFI-027-Test-Cases.md.
All Graph API calls are mocked — no live network access.
"""

import time
from unittest.mock import MagicMock, patch, call

import pytest
import requests

from accia_s360.config import S360Config
from accia_s360.exceptions import S360ApiError, S360AuthError
from accia_s360.models import OrgPerson, OrgTree
from accia_s360.endpoints.graph import GraphEndpoint


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def config():
    return S360Config()


@pytest.fixture
def mock_token():
    return "fake-graph-token-12345"


@pytest.fixture
def graph(config, mock_token):
    return GraphEndpoint(config, lambda: mock_token)


# ---------------------------------------------------------------------------
# Helpers — mock Graph API JSON responses
# ---------------------------------------------------------------------------

def _person_json(alias: str, name: str | None = None, title: str = "Engineer",
                 dept: str = "Engineering", oid: str = "oid-1") -> dict:
    """Build a Graph-style user dict."""
    return {
        "displayName": name or alias.title(),
        "mailNickname": alias,
        "jobTitle": title,
        "department": dept,
        "id": oid,
    }


def _ok(json_body, status=200, headers=None):
    """Build a mock requests.Response."""
    resp = MagicMock(spec=requests.Response)
    resp.status_code = status
    resp.json.return_value = json_body
    resp.headers = headers or {}
    resp.text = "ok"
    return resp


def _err(status, body="error", headers=None):
    resp = MagicMock(spec=requests.Response)
    resp.status_code = status
    resp.json.return_value = {"error": {"message": body}}
    resp.headers = headers or {}
    resp.text = body
    return resp


# ========================== AC-1: get_manager_chain ==========================

class TestGetManagerChain:
    """T01–T06: Manager chain upward."""

    @patch("accia_s360.endpoints.graph.requests.get")
    def test_returns_ordered_list(self, mock_get, graph):
        """T01: 3-level chain user → mgr1 → mgr2 → CEO (404)."""
        mock_get.side_effect = [
            _ok(_person_json("mgr1", "Manager One", oid="oid-mgr1")),   # user's manager
            _ok(_person_json("mgr2", "Manager Two", oid="oid-mgr2")),   # mgr1's manager
            _ok(_person_json("ceo", "The CEO", oid="oid-ceo")),         # mgr2's manager
            _err(404),                                                    # ceo's manager → 404
        ]
        chain = graph.get_manager_chain("testuser")
        assert len(chain) == 3
        assert chain[0].alias == "mgr1"
        assert chain[1].alias == "mgr2"
        assert chain[2].alias == "ceo"

    @patch("accia_s360.endpoints.graph.requests.get")
    def test_single_manager(self, mock_get, graph):
        """T02: User's manager's manager returns 404."""
        mock_get.side_effect = [
            _ok(_person_json("boss", "The Boss")),
            _err(404),
        ]
        chain = graph.get_manager_chain("worker")
        assert len(chain) == 1
        assert chain[0].alias == "boss"

    @patch("accia_s360.endpoints.graph.requests.get")
    def test_ceo_has_no_manager(self, mock_get, graph):
        """T03: Target is CEO — first /manager returns 404."""
        mock_get.side_effect = [
            _err(404),                               # /manager → 404
            _ok(_person_json("satyan", "CEO")),      # verify user exists → 200
        ]
        chain = graph.get_manager_chain("satyan")
        assert chain == []

    @patch("accia_s360.endpoints.graph.requests.get")
    def test_org_person_fields(self, mock_get, graph):
        """T04: Verify all OrgPerson fields populated."""
        mock_get.side_effect = [
            _ok(_person_json("mgr1", "Alice Manager", "VP Eng", "Engineering", "abc-123")),
            _err(404),
        ]
        chain = graph.get_manager_chain("testuser")
        p = chain[0]
        assert p.alias == "mgr1"
        assert p.display_name == "Alice Manager"
        assert p.job_title == "VP Eng"
        assert p.department == "Engineering"
        assert p.object_id == "abc-123"

    @patch("accia_s360.endpoints.graph.requests.get")
    def test_alias_uses_upn_format(self, mock_get, graph):
        """T05: Request URL uses {alias}@microsoft.com."""
        mock_get.side_effect = [
            _ok(_person_json("mgr")),  # /manager → 200
            _err(404),                  # mgr's /manager → 404 (terminate)
        ]
        graph.get_manager_chain("testalias")
        url = mock_get.call_args_list[0].args[0]
        assert "testalias@microsoft.com" in url

    @patch("accia_s360.endpoints.graph.requests.get")
    def test_cycle_protection(self, mock_get, graph):
        """T06: Graph cycle A→B→A terminates safely."""
        mock_get.side_effect = [
            _ok(_person_json("bob", oid="oid-bob")),
            _ok(_person_json("alice", oid="oid-alice")),
            _ok(_person_json("bob", oid="oid-bob")),  # cycle!
        ]
        chain = graph.get_manager_chain("alice")
        # Should stop when it sees a repeated alias
        assert len(chain) <= 2


# ======================== AC-2: get_direct_reports ========================

class TestGetDirectReports:
    """T07–T14: Direct reports with SC ALT filtering."""

    @patch("accia_s360.endpoints.graph.requests.get")
    def test_returns_list(self, mock_get, graph):
        """T07: 3 direct reports, no SC ALTs."""
        mock_get.return_value = _ok({
            "value": [
                _person_json("alice"),
                _person_json("bob"),
                _person_json("carol"),
            ]
        })
        reports = graph.get_direct_reports("manager1")
        assert len(reports) == 3

    @patch("accia_s360.endpoints.graph.requests.get")
    def test_filters_sc_alt_by_alias(self, mock_get, graph):
        """T08: SC ALT alias sc-pj467 filtered out."""
        mock_get.return_value = _ok({
            "value": [
                _person_json("alice"),
                _person_json("sc-pj467", "Shadow Alt"),
            ]
        })
        reports = graph.get_direct_reports("manager1")
        assert len(reports) == 1
        assert reports[0].alias == "alice"

    @patch("accia_s360.endpoints.graph.requests.get")
    def test_filters_sc_alt_by_display_name(self, mock_get, graph):
        """T09: Display name containing 'NON EA SC ALT' filtered."""
        mock_get.return_value = _ok({
            "value": [
                _person_json("alice"),
                _person_json("normalias", "Brent Jensen (NON EA SC ALT)"),
            ]
        })
        reports = graph.get_direct_reports("manager1")
        assert len(reports) == 1
        assert reports[0].alias == "alice"

    @patch("accia_s360.endpoints.graph.requests.get")
    def test_sc_alt_case_insensitive(self, mock_get, graph):
        """T10: Aliases SC-xxx, sc-xxx, Sc-xxx all filtered."""
        mock_get.return_value = _ok({
            "value": [
                _person_json("SC-upper"),
                _person_json("sc-lower"),
                _person_json("Sc-mixed"),
                _person_json("realuser"),
            ]
        })
        reports = graph.get_direct_reports("manager1")
        assert len(reports) == 1
        assert reports[0].alias == "realuser"

    @patch("accia_s360.endpoints.graph.requests.get")
    def test_exclude_sc_alts_false(self, mock_get, graph):
        """T11: exclude_sc_alts=False includes SC ALTs."""
        mock_get.return_value = _ok({
            "value": [
                _person_json("alice"),
                _person_json("sc-shadow"),
            ]
        })
        reports = graph.get_direct_reports("manager1", exclude_sc_alts=False)
        assert len(reports) == 2

    @patch("accia_s360.endpoints.graph.requests.get")
    def test_empty_reports(self, mock_get, graph):
        """T12: User has no direct reports."""
        mock_get.return_value = _ok({"value": []})
        reports = graph.get_direct_reports("leafuser")
        assert reports == []

    @patch("accia_s360.endpoints.graph.requests.get")
    def test_pagination(self, mock_get, graph):
        """T13: @odata.nextLink pagination combines pages."""
        page1 = _ok({
            "value": [_person_json("alice")],
            "@odata.nextLink": "https://graph.microsoft.com/v1.0/next-page",
        })
        page2 = _ok({
            "value": [_person_json("bob")],
        })
        mock_get.side_effect = [page1, page2]
        reports = graph.get_direct_reports("manager1")
        assert len(reports) == 2
        assert reports[0].alias == "alice"
        assert reports[1].alias == "bob"

    @patch("accia_s360.endpoints.graph.requests.get")
    def test_org_person_fields_from_reports(self, mock_get, graph):
        """T14: Each OrgPerson from reports has all required fields."""
        mock_get.return_value = _ok({
            "value": [_person_json("alice", "Alice A", "SDE II", "Cloud", "oid-alice")],
        })
        reports = graph.get_direct_reports("manager1")
        p = reports[0]
        assert p.alias == "alice"
        assert p.display_name == "Alice A"
        assert p.job_title == "SDE II"
        assert p.department == "Cloud"
        assert p.object_id == "oid-alice"


# ========================== AC-3: get_org_tree ============================

class TestGetOrgTree:
    """T15–T20: Nested org tree."""

    @patch("accia_s360.endpoints.graph.requests.get")
    def test_explicit_depth_2(self, mock_get, graph):
        """T15: depth=2 returns 2 levels of reports."""
        # get_user call for root
        root_resp = _ok(_person_json("root", "Root User"))
        # directReports for root (depth 1)
        root_reports = _ok({"value": [_person_json("d1"), _person_json("d2")]})
        # directReports for d1 (depth 2)
        d1_reports = _ok({"value": [_person_json("d1a")]})
        # directReports for d2 (depth 2)
        d2_reports = _ok({"value": [_person_json("d2a"), _person_json("d2b")]})

        mock_get.side_effect = [root_resp, root_reports, d1_reports, d2_reports]
        tree = graph.get_org_tree("root", depth=2)

        assert tree.person.alias == "root"
        assert len(tree.direct_reports) == 2
        assert len(tree.direct_reports[0].direct_reports) == 1
        assert len(tree.direct_reports[1].direct_reports) == 2

    @patch("accia_s360.endpoints.graph.requests.get")
    def test_default_depth_none_full_tree(self, mock_get, graph):
        """T15b: depth=None (default) fetches the entire tree."""
        # 3-level tree: root -> d1 -> d1a (leaf)
        root_resp = _ok(_person_json("root", "Root User"))
        root_reports = _ok({"value": [_person_json("d1")]})
        d1_reports = _ok({"value": [_person_json("d1a")]})
        d1a_reports = _ok({"value": []})  # leaf — no reports

        mock_get.side_effect = [root_resp, root_reports, d1_reports, d1a_reports]
        tree = graph.get_org_tree("root")  # no depth arg → None → full tree

        assert tree.person.alias == "root"
        assert len(tree.direct_reports) == 1
        assert tree.direct_reports[0].person.alias == "d1"
        assert len(tree.direct_reports[0].direct_reports) == 1
        assert tree.direct_reports[0].direct_reports[0].person.alias == "d1a"
        assert tree.direct_reports[0].direct_reports[0].direct_reports == []

    @patch("accia_s360.endpoints.graph.requests.get")
    def test_depth_0(self, mock_get, graph):
        """T16: depth=0 returns person only, no reports."""
        mock_get.return_value = _ok(_person_json("solo"))
        tree = graph.get_org_tree("solo", depth=0)
        assert tree.person.alias == "solo"
        assert tree.direct_reports == []

    @patch("accia_s360.endpoints.graph.requests.get")
    def test_depth_1(self, mock_get, graph):
        """T17: depth=1 returns person + directs, no sub-reports."""
        root_resp = _ok(_person_json("mgr"))
        reports_resp = _ok({"value": [_person_json("emp1"), _person_json("emp2")]})
        mock_get.side_effect = [root_resp, reports_resp]
        tree = graph.get_org_tree("mgr", depth=1)
        assert len(tree.direct_reports) == 2
        assert tree.direct_reports[0].direct_reports == []
        assert tree.direct_reports[1].direct_reports == []

    @patch("accia_s360.endpoints.graph.requests.get")
    def test_filters_sc_alts(self, mock_get, graph):
        """T18: SC ALTs excluded at all levels."""
        root_resp = _ok(_person_json("mgr"))
        reports_resp = _ok({
            "value": [
                _person_json("real1"),
                _person_json("sc-shadow", "Shadow (NON EA SC ALT)"),
            ]
        })
        mock_get.side_effect = [root_resp, reports_resp]
        tree = graph.get_org_tree("mgr", depth=1)
        assert len(tree.direct_reports) == 1
        assert tree.direct_reports[0].person.alias == "real1"

    @patch("accia_s360.endpoints.graph.requests.get")
    def test_person_is_target_user(self, mock_get, graph):
        """T19: OrgTree.person is the target alias."""
        mock_get.return_value = _ok(_person_json("target"))
        tree = graph.get_org_tree("target", depth=0)
        assert tree.person.alias == "target"

    @patch("accia_s360.endpoints.graph.requests.get")
    def test_leaf_nodes_have_empty_reports(self, mock_get, graph):
        """T20: Leaf nodes at max depth have empty direct_reports."""
        root_resp = _ok(_person_json("mgr"))
        reports_resp = _ok({"value": [_person_json("leaf")]})
        mock_get.side_effect = [root_resp, reports_resp]
        tree = graph.get_org_tree("mgr", depth=1)
        assert tree.direct_reports[0].direct_reports == []


# ====================== AC-4: Error handling & retry ======================

class TestErrorHandling:
    """T21–T30: Auth errors, API errors, rate limiting, network failures."""

    @patch("accia_s360.endpoints.graph.requests.get")
    def test_auth_error_401(self, mock_get, graph):
        """T21: 401 raises S360AuthError."""
        mock_get.return_value = _err(401)
        with pytest.raises(S360AuthError):
            graph.get_manager_chain("someone")

    @patch("accia_s360.endpoints.graph.requests.get")
    def test_forbidden_403(self, mock_get, graph):
        """T22: 403 raises S360AuthError."""
        mock_get.return_value = _err(403)
        with pytest.raises(S360AuthError):
            graph.get_manager_chain("someone")

    @patch("accia_s360.endpoints.graph.requests.get")
    def test_api_error_500(self, mock_get, graph):
        """T23: 500 raises S360ApiError with status code."""
        mock_get.return_value = _err(500, "Internal Server Error")
        with pytest.raises(S360ApiError) as exc_info:
            graph.get_manager_chain("someone")
        assert exc_info.value.status_code == 500

    @patch("accia_s360.endpoints.graph.time.sleep")
    @patch("accia_s360.endpoints.graph.requests.get")
    def test_rate_limit_429_retries(self, mock_get, mock_sleep, graph):
        """T24: 429 then 200 succeeds on retry."""
        mock_get.side_effect = [
            _err(429, headers={"Retry-After": "1"}),
            _ok(_person_json("mgr")),
            _err(404),  # terminate chain
        ]
        chain = graph.get_manager_chain("user1")
        assert len(chain) == 1

    @patch("accia_s360.endpoints.graph.time.sleep")
    @patch("accia_s360.endpoints.graph.requests.get")
    def test_rate_limit_respects_retry_after(self, mock_get, mock_sleep, graph):
        """T25: Waits Retry-After seconds before retry."""
        mock_get.side_effect = [
            _err(429, headers={"Retry-After": "2"}),
            _ok(_person_json("mgr")),
            _err(404),
        ]
        graph.get_manager_chain("user1")
        mock_sleep.assert_called_with(2)

    @patch("accia_s360.endpoints.graph.time.sleep")
    @patch("accia_s360.endpoints.graph.requests.get")
    def test_rate_limit_max_3_retries(self, mock_get, mock_sleep, graph):
        """T26: After 3 retries of 429 raises S360ApiError."""
        mock_get.return_value = _err(429, headers={"Retry-After": "1"})
        with pytest.raises(S360ApiError):
            graph.get_manager_chain("user1")
        assert mock_sleep.call_count == 3

    @patch("accia_s360.endpoints.graph.time.sleep")
    @patch("accia_s360.endpoints.graph.requests.get")
    def test_rate_limit_exponential_backoff(self, mock_get, mock_sleep, graph):
        """T27: Sleep durations increase exponentially."""
        mock_get.side_effect = [
            _err(429),
            _err(429),
            _err(429),
            _ok(_person_json("mgr")),
            _err(404),
        ]
        graph.get_manager_chain("user1")
        delays = [c.args[0] for c in mock_sleep.call_args_list]
        # Each delay should be >= the previous
        for i in range(1, len(delays)):
            assert delays[i] >= delays[i - 1]

    @patch("accia_s360.endpoints.graph.requests.get")
    def test_network_error(self, mock_get, graph):
        """T28: ConnectionError raises S360ApiError."""
        mock_get.side_effect = requests.ConnectionError("Network down")
        with pytest.raises(S360ApiError):
            graph.get_manager_chain("someone")

    @patch("accia_s360.endpoints.graph.requests.get")
    def test_timeout_error(self, mock_get, graph):
        """T29: Timeout raises S360ApiError."""
        mock_get.side_effect = requests.Timeout("Timed out")
        with pytest.raises(S360ApiError):
            graph.get_manager_chain("someone")

    @patch("accia_s360.endpoints.graph.requests.get")
    def test_user_not_found_404(self, mock_get, graph):
        """T30: 404 on directReports raises S360ApiError (user not found)."""
        mock_get.return_value = _err(404)
        with pytest.raises(S360ApiError):
            graph.get_direct_reports("nonexistent")


# ===================== AC-5: Model & infrastructure =======================

class TestModels:
    """T31–T34: OrgPerson factory, OrgTree structure, request params."""

    def test_org_person_from_graph_response(self):
        """T31: from_graph_response() creates correct OrgPerson."""
        data = _person_json("alice", "Alice Adams", "SDE II", "Cloud", "abc-123")
        p = OrgPerson.from_graph_response(data)
        assert p.alias == "alice"
        assert p.display_name == "Alice Adams"
        assert p.job_title == "SDE II"
        assert p.department == "Cloud"
        assert p.object_id == "abc-123"

    def test_org_person_missing_fields(self):
        """T32: Missing jobTitle/department default to None."""
        data = {"mailNickname": "bob", "displayName": "Bob", "id": "x"}
        p = OrgPerson.from_graph_response(data)
        assert p.alias == "bob"
        assert p.job_title is None
        assert p.department is None

    def test_org_tree_recursive_structure(self):
        """T33: OrgTree nests correctly."""
        leaf = OrgTree(person=OrgPerson(alias="leaf", display_name="Leaf"))
        root = OrgTree(
            person=OrgPerson(alias="root", display_name="Root"),
            direct_reports=[leaf],
        )
        assert root.direct_reports[0].person.alias == "leaf"
        assert root.direct_reports[0].direct_reports == []

    @patch("accia_s360.endpoints.graph.requests.get")
    def test_graph_select_params(self, mock_get, graph):
        """T34: Requests include correct $select parameter."""
        mock_get.side_effect = [
            _ok(_person_json("mgr")),  # /manager → 200
            _err(404),                  # mgr's /manager → 404 (terminate chain)
        ]
        graph.get_manager_chain("testalias")
        url = mock_get.call_args_list[0].args[0]
        assert "$select=" in url
        assert "displayName" in url
        assert "mailNickname" in url
