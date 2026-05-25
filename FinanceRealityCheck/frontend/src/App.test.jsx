import { fireEvent, render, screen } from "@testing-library/react";
import App from "./App";

function mockFetchByRoute(routes) {
  global.fetch = vi.fn(async (url) => {
    for (const route of routes) {
      if (String(url).endsWith(route.path)) {
        return {
          ok: true,
          status: 200,
          json: async () => route.body,
        };
      }
    }

    return {
      ok: false,
      status: 404,
      json: async () => ({}),
    };
  });
}

describe("App", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("renders health status and version on landing", async () => {
    mockFetchByRoute([
      { path: "/health", body: { status: "ok", version: "0.5.0" } },
    ]);

    render(<App />);

    expect(await screen.findByText("ok")).toBeInTheDocument();
    expect(screen.getByText("0.5.0")).toBeInTheDocument();
  });

  it("renders planner summary capabilities deterministically", async () => {
    mockFetchByRoute([
      { path: "/health", body: { status: "ok", version: "0.5.0" } },
      {
        path: "/planner/summary",
        body: {
          interface: "local-web-api",
          capabilities: ["unusual_alerts", "budget_alerts", "tax_threshold_alerts"],
        },
      },
    ]);

    render(<App />);

    fireEvent.click(screen.getByRole("button", { name: "Planner Summary" }));

    expect(await screen.findByText(/local-web-api/)).toBeInTheDocument();
    expect(screen.getByText("budget_alerts")).toBeInTheDocument();
    expect(screen.getByText("tax_threshold_alerts")).toBeInTheDocument();
    expect(screen.getByText("unusual_alerts")).toBeInTheDocument();
  });

  it("shows deterministic unavailable-api error state", async () => {
    global.fetch = vi.fn(async () => {
      throw new Error("connectivity");
    });

    render(<App />);

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "API unavailable. Ensure local API is running on http://127.0.0.1:8000.",
    );
    expect(screen.getByRole("button", { name: "Retry" })).toBeInTheDocument();
  });
});
