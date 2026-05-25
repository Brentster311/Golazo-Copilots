from __future__ import annotations

from fastapi.testclient import TestClient

from finance_planner.api import create_app, main


def test_health_endpoint_returns_deterministic_status_payload() -> None:
    app = create_app()
    client = TestClient(app)

    first = client.get("/health")
    second = client.get("/health")

    assert first.status_code == 200, "Expected /health endpoint to return HTTP 200."
    assert second.status_code == 200, "Expected repeated /health call to return HTTP 200."
    assert first.json() == second.json(), "Expected deterministic /health payload across repeated reads."
    assert first.json()["status"] == "ok", "Expected /health payload status field to be 'ok'."
    assert "version" in first.json(), "Expected /health payload to include package version field."


def test_planner_summary_endpoint_returns_expected_capability_contract() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.get("/planner/summary")

    assert response.status_code == 200, "Expected /planner/summary endpoint to return HTTP 200."
    payload = response.json()
    assert payload["interface"] == "local-web-api", "Expected summary interface contract to identify local web API surface."

    expected_capabilities = {
        "budget_alerts",
        "unusual_alerts",
        "goal_drift_alerts",
        "allocation_recommendations",
        "tax_threshold_alerts",
    }
    assert set(payload["capabilities"]) == expected_capabilities, "Expected summary capabilities to match implemented planner feature set."


def test_main_runner_accepts_host_and_port_arguments(monkeypatch) -> None:
    captured: dict[str, int | str] = {}

    def fake_run_api_server(host: str, port: int) -> None:
        captured["host"] = host
        captured["port"] = port

    monkeypatch.setattr("finance_planner.api.run_api_server", fake_run_api_server)
    main(["--host", "127.0.0.1", "--port", "8000"])

    assert captured == {
        "host": "127.0.0.1",
        "port": 8000,
    }, "Expected CLI runner to pass host/port arguments to API server bootstrap."
