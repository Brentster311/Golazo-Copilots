from __future__ import annotations

import argparse
import logging
from datetime import UTC, datetime
from importlib.metadata import PackageNotFoundError, version
from typing import Sequence

from fastapi import FastAPI

LOGGER = logging.getLogger("finance_planner.api")
_PACKAGE_NAME = "finance-planner"


def _package_version() -> str:
    try:
        return version(_PACKAGE_NAME)
    except PackageNotFoundError:
        return "0.0.0"


def create_app() -> FastAPI:
    app = FastAPI(title="Finance Planner API", version=_package_version())
    app.state.started_at = datetime.now(tz=UTC).isoformat()
    app.state.health_hits = 0

    @app.get("/health")
    def health() -> dict[str, str]:
        app.state.health_hits += 1
        return {
            "status": "ok",
            "version": app.version,
        }

    @app.get("/planner/summary")
    def planner_summary() -> dict[str, object]:
        return {
            "interface": "local-web-api",
            "capabilities": [
                "allocation_recommendations",
                "budget_alerts",
                "goal_drift_alerts",
                "tax_threshold_alerts",
                "unusual_alerts",
            ],
        }

    return app


def run_api_server(host: str, port: int) -> None:
    started_at = datetime.now(tz=UTC).isoformat()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    LOGGER.info("Starting Finance Planner API host=%s port=%s started_at=%s", host, port, started_at)

    import uvicorn

    uvicorn.run("finance_planner.api:create_app", host=host, port=port, factory=True, log_level="info")


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Finance Planner local API server")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host (default: 127.0.0.1)")
    parser.add_argument("--port", default=8000, type=int, help="Bind port (default: 8000)")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    args = _parse_args(argv)
    run_api_server(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
