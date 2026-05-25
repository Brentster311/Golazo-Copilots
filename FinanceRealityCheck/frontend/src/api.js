const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

async function requestJson(path) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { Accept: "application/json" },
  });

  if (!response.ok) {
    throw new Error(`request_failed_${response.status}`);
  }

  return response.json();
}

export function fetchHealth() {
  return requestJson("/health");
}

export function fetchPlannerSummary() {
  return requestJson("/planner/summary");
}
