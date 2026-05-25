import { useEffect, useMemo, useState } from "react";
import { fetchHealth, fetchPlannerSummary } from "./api";
import "./styles.css";

const UI_ERROR_TEXT = "API unavailable. Ensure local API is running on http://127.0.0.1:8000.";

const telemetry = {
  startupSuccessCount: 0,
  startupFailureCount: 0,
  apiConnectivityFailureCount: 0,
};

function isHealthPayload(payload) {
  return payload && typeof payload.status === "string" && typeof payload.version === "string";
}

function isSummaryPayload(payload) {
  return (
    payload &&
    typeof payload.interface === "string" &&
    Array.isArray(payload.capabilities) &&
    payload.capabilities.every((item) => typeof item === "string")
  );
}

export default function App() {
  const [view, setView] = useState("health");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [payload, setPayload] = useState(null);
  const [retryNonce, setRetryNonce] = useState(0);

  useEffect(() => {
    telemetry.startupSuccessCount += 1;
    console.info("ui_startup", {
      startupSuccessCount: telemetry.startupSuccessCount,
      startupFailureCount: telemetry.startupFailureCount,
    });
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function loadCurrentView() {
      setLoading(true);
      setError("");

      try {
        const result = view === "health" ? await fetchHealth() : await fetchPlannerSummary();
        if (!cancelled) {
          setPayload(result);
          setLoading(false);
        }
      } catch {
        telemetry.apiConnectivityFailureCount += 1;
        telemetry.startupFailureCount += 1;
        console.warn("ui_api_unavailable", {
          view,
          startupFailureCount: telemetry.startupFailureCount,
          apiConnectivityFailureCount: telemetry.apiConnectivityFailureCount,
        });

        if (!cancelled) {
          setPayload(null);
          setError(UI_ERROR_TEXT);
          setLoading(false);
        }
      }
    }

    loadCurrentView();
    return () => {
      cancelled = true;
    };
  }, [view, retryNonce]);

  const sortedCapabilities = useMemo(() => {
    if (!isSummaryPayload(payload)) {
      return [];
    }
    return [...payload.capabilities].sort((a, b) => a.localeCompare(b));
  }, [payload]);

  return (
    <main className="shell-root">
      <section className="shell-card">
        <header className="shell-header">
          <h1>Finance Planner UI Shell</h1>
          <p>Desktop-first local interface for planner API validation.</p>
        </header>

        <nav className="shell-nav" aria-label="Planner views">
          <button
            type="button"
            className={view === "health" ? "active" : ""}
            aria-pressed={view === "health"}
            onClick={() => setView("health")}
          >
            Health
          </button>
          <button
            type="button"
            className={view === "summary" ? "active" : ""}
            aria-pressed={view === "summary"}
            onClick={() => setView("summary")}
          >
            Planner Summary
          </button>
        </nav>

        <section className="shell-content" aria-live="polite">
          {loading ? <p>Loading...</p> : null}

          {!loading && error ? (
            <div className="shell-error" role="alert">
              <p>{error}</p>
              <button type="button" onClick={() => setRetryNonce((value) => value + 1)}>
                Retry
              </button>
            </div>
          ) : null}

          {!loading && !error && view === "health" ? (
            isHealthPayload(payload) ? (
              <dl>
                <div>
                  <dt>Status</dt>
                  <dd>{payload.status}</dd>
                </div>
                <div>
                  <dt>Version</dt>
                  <dd>{payload.version}</dd>
                </div>
              </dl>
            ) : (
              <p className="shell-error-inline">Contract error: invalid /health payload.</p>
            )
          ) : null}

          {!loading && !error && view === "summary" ? (
            isSummaryPayload(payload) ? (
              <div>
                <p>
                  <strong>Interface:</strong> {payload.interface}
                </p>
                <h2>Capabilities</h2>
                <ul>
                  {sortedCapabilities.map((capability) => (
                    <li key={capability}>{capability}</li>
                  ))}
                </ul>
              </div>
            ) : (
              <p className="shell-error-inline">Contract error: invalid /planner/summary payload.</p>
            )
          ) : null}
        </section>
      </section>
    </main>
  );
}
