import { render, screen, waitFor, fireEvent, act } from "@testing-library/react";
import { expect, test, vi, beforeEach, afterEach } from "vitest";
import { App } from "./App";

// Mock fetch globally
const mockFetch = vi.fn();

beforeEach(() => {
  vi.useFakeTimers({ shouldAdvanceTime: true });
  global.fetch = mockFetch;
  mockFetch.mockReset();

  // Default: listSubmissions returns empty
  mockFetch.mockImplementation((url: string) => {
    if (typeof url === "string" && url.includes("/submissions") && !url.includes("/upload-url") && !url.includes("/start")) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ items: [], nextToken: null }),
      });
    }
    return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
  });
});

afterEach(() => {
  vi.useRealTimers();
  vi.restoreAllMocks();
});

test("renders the app shell with brand and title", async () => {
  render(<App />);
  expect(screen.getByLabelText("Marsh")).toBeDefined();
  expect(screen.getByText("RiskLens")).toBeDefined();
});

test("renders logout action after auth is ready", async () => {
  render(<App />);
  await waitFor(() => {
    expect(screen.getByRole("button", { name: "Log out" })).toBeDefined();
  });
});

test("renders the upload panel", async () => {
  render(<App />);
  expect(screen.getByText("Upload Submission")).toBeDefined();
  expect(
    screen.getByText(/Drag and drop a file, or click to browse/),
  ).toBeDefined();
  expect(screen.getByText(/PDF, PNG, JPEG, or TXT/)).toBeDefined();
});

test("renders the recent submissions panel with empty state after loading", async () => {
  render(<App />);
  await waitFor(() => {
    expect(screen.getByText("No submissions yet")).toBeDefined();
  });
});

test("renders the status area in idle state", async () => {
  render(<App />);
  expect(screen.getByText("No active processing")).toBeDefined();
});

test("shows loading skeleton while fetching submissions", () => {
  // Make fetch hang to keep loading state
  mockFetch.mockImplementation(() => new Promise(() => {}));
  render(<App />);
  expect(screen.getByLabelText("Loading submissions")).toBeDefined();
});

test("upload flow triggers API calls in sequence", async () => {
  const uploadUrlResponse = {
    submissionId: "sub-123",
    uploadUrl: "https://s3.example.com/presigned",
    objectKey: "submissions/sub-123/raw/test.pdf",
    expiresInSeconds: 900,
    maxFileSizeBytes: 10000000,
  };

  const startResponse = {
    submissionId: "sub-123",
    status: "QUEUED",
  };

  const statusResponseReady = {
    submissionId: "sub-123",
    status: "READY",
    createdAt: "2026-05-24T11:00:00Z",
    updatedAt: "2026-05-24T11:02:00Z",
    progress: null,
    file: { fileName: "test.pdf", contentType: "application/pdf" },
    error: null,
  };

  mockFetch.mockImplementation((url: string, options?: RequestInit) => {
    // listSubmissions (called on mount and after completion)
    if (typeof url === "string" && url.match(/\/submissions(\?|$)/) && (!options || options.method === "GET")) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ items: [], nextToken: null }),
      });
    }
    // upload-url
    if (typeof url === "string" && url.includes("/upload-url")) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve(uploadUrlResponse),
      });
    }
    // S3 PUT
    if (typeof url === "string" && url.includes("s3.example.com")) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    }
    // start
    if (typeof url === "string" && url.includes("/start")) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve(startResponse),
      });
    }
    // status poll
    if (typeof url === "string" && url.includes("/sub-123") && !url.includes("/start")) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve(statusResponseReady),
      });
    }
    return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
  });

  render(<App />);

  // Wait for initial load
  await waitFor(() => {
    expect(screen.getByText("No submissions yet")).toBeDefined();
  });

  // Simulate file selection via the hidden input
  const file = new File(["test content"], "test.pdf", {
    type: "application/pdf",
  });
  const fileInput = screen.getByLabelText("Select file") as HTMLInputElement;

  await act(async () => {
    fireEvent.change(fileInput, { target: { files: [file] } });
  });

  // Click upload button
  const uploadButton = screen.getByRole("button", { name: "Upload" });
  await act(async () => {
    fireEvent.click(uploadButton);
  });

  // Advance timers to allow polling
  await act(async () => {
    await vi.advanceTimersByTimeAsync(100);
  });

  // Wait for the upload flow to complete (polling returns READY)
  await waitFor(() => {
    expect(screen.getByText("Processing Complete")).toBeDefined();
  });

  // Verify API calls were made (at least upload-url, S3 PUT, start, status poll)
  const urls = mockFetch.mock.calls.map((c) => c[0] as string);
  expect(urls.some((u) => u.includes("/upload-url"))).toBe(true);
  expect(urls.some((u) => u.includes("s3.example.com"))).toBe(true);
  expect(urls.some((u) => u.includes("/start"))).toBe(true);
});

test("error state renders error message", async () => {
  mockFetch.mockImplementation((url: string, options?: RequestInit) => {
    // listSubmissions
    if (typeof url === "string" && url.match(/\/submissions(\?|$)/) && (!options || options.method === "GET")) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ items: [], nextToken: null }),
      });
    }
    // upload-url fails
    if (typeof url === "string" && url.includes("/upload-url")) {
      return Promise.resolve({
        ok: false,
        status: 400,
        json: () =>
          Promise.resolve({ message: "Unsupported content type" }),
      });
    }
    return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
  });

  render(<App />);

  await waitFor(() => {
    expect(screen.getByText("No submissions yet")).toBeDefined();
  });

  // Upload a file that the API rejects
  const file = new File(["data"], "test.pdf", { type: "application/pdf" });
  const fileInput = screen.getByLabelText("Select file") as HTMLInputElement;

  await act(async () => {
    fireEvent.change(fileInput, { target: { files: [file] } });
  });

  const uploadButton = screen.getByRole("button", { name: "Upload" });
  await act(async () => {
    fireEvent.click(uploadButton);
  });

  await act(async () => {
    await vi.advanceTimersByTimeAsync(100);
  });

  await waitFor(() => {
    expect(screen.getByText("Unsupported content type")).toBeDefined();
  });
});

test("NEEDS_REVIEW terminal state shows review affordance and loads summary", async () => {
  const uploadUrlResponse = {
    submissionId: "sub-nr",
    uploadUrl: "https://s3.example.com/presigned",
    objectKey: "submissions/sub-nr/raw/test.pdf",
    expiresInSeconds: 900,
    maxFileSizeBytes: 10000000,
  };
  const statusNeedsReview = {
    submissionId: "sub-nr",
    status: "NEEDS_REVIEW",
    createdAt: "2026-05-24T11:00:00Z",
    updatedAt: "2026-05-24T11:02:00Z",
    progress: null,
    file: { fileName: "needs.pdf", contentType: "application/pdf" },
    error: null,
  };
  const summaryResponse = {
    submissionId: "sub-nr",
    status: "NEEDS_REVIEW",
    extracted: {
      insuredName: "Example Manufacturing LLC",
      industry: "Light manufacturing",
      missingFields: ["constructionYear"],
    },
    hazards: { topHazards: ["Wildfire"], femaRiskRating: "Relatively High" },
    aiBrief: {
      executiveSummary: "Needs construction year confirmation.",
      riskFlags: ["Construction year missing."],
      questionsForBroker: ["Confirm construction year."],
      confidence: "medium",
    },
    sources: [{ name: "FEMA National Risk Index", url: "https://hazards.fema.gov" }],
  };

  mockFetch.mockImplementation((url: string, options?: RequestInit) => {
    if (typeof url === "string" && url.includes("/summary")) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve(summaryResponse) });
    }
    if (typeof url === "string" && url.match(/\/submissions(\?|$)/) && (!options || options.method === "GET")) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ items: [], nextToken: null }) });
    }
    if (typeof url === "string" && url.includes("/upload-url")) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve(uploadUrlResponse) });
    }
    if (typeof url === "string" && url.includes("s3.example.com")) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    }
    if (typeof url === "string" && url.includes("/start")) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ submissionId: "sub-nr", status: "QUEUED" }) });
    }
    if (typeof url === "string" && url.includes("/sub-nr") && !url.includes("/start")) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve(statusNeedsReview) });
    }
    return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
  });

  render(<App />);
  await waitFor(() => expect(screen.getByText("No submissions yet")).toBeDefined());

  const file = new File(["data"], "needs.pdf", { type: "application/pdf" });
  const fileInput = screen.getByLabelText("Select file") as HTMLInputElement;
  await act(async () => {
    fireEvent.change(fileInput, { target: { files: [file] } });
  });
  await act(async () => {
    fireEvent.click(screen.getByRole("button", { name: "Upload" }));
  });
  await act(async () => {
    await vi.advanceTimersByTimeAsync(100);
  });

  await waitFor(() => expect(screen.getByText("Review Required")).toBeDefined());

  // Open the summary
  await act(async () => {
    fireEvent.click(screen.getByRole("button", { name: "Review Submission" }));
  });

  await waitFor(() => {
    expect(screen.getByText("AI Triage Brief")).toBeDefined();
  });
  // Broker-review framing must be present.
  expect(screen.getByText(/AI-generated draft for broker review/)).toBeDefined();
  // Missing field surfaced.
  expect(screen.getByText("constructionYear")).toBeDefined();
});

test("FAILED terminal state offers a retry affordance", async () => {
  const uploadUrlResponse = {
    submissionId: "sub-fail",
    uploadUrl: "https://s3.example.com/presigned",
    objectKey: "submissions/sub-fail/raw/test.pdf",
    expiresInSeconds: 900,
    maxFileSizeBytes: 10000000,
  };
  const statusFailed = {
    submissionId: "sub-fail",
    status: "FAILED",
    createdAt: "2026-05-24T11:00:00Z",
    updatedAt: "2026-05-24T11:02:00Z",
    progress: null,
    file: { fileName: "broken.pdf", contentType: "application/pdf" },
    error: "OCR engine could not read the document.",
  };

  mockFetch.mockImplementation((url: string, options?: RequestInit) => {
    if (typeof url === "string" && url.match(/\/submissions(\?|$)/) && (!options || options.method === "GET")) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ items: [], nextToken: null }) });
    }
    if (typeof url === "string" && url.includes("/upload-url")) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve(uploadUrlResponse) });
    }
    if (typeof url === "string" && url.includes("s3.example.com")) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    }
    if (typeof url === "string" && url.includes("/start")) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ submissionId: "sub-fail", status: "QUEUED" }) });
    }
    if (typeof url === "string" && url.includes("/sub-fail") && !url.includes("/start")) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve(statusFailed) });
    }
    return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
  });

  render(<App />);
  await waitFor(() => expect(screen.getByText("No submissions yet")).toBeDefined());

  const file = new File(["data"], "broken.pdf", { type: "application/pdf" });
  const fileInput = screen.getByLabelText("Select file") as HTMLInputElement;
  await act(async () => {
    fireEvent.change(fileInput, { target: { files: [file] } });
  });
  await act(async () => {
    fireEvent.click(screen.getByRole("button", { name: "Upload" }));
  });
  await act(async () => {
    await vi.advanceTimersByTimeAsync(100);
  });

  await waitFor(() => expect(screen.getByText("Processing Failed")).toBeDefined());
  expect(screen.getByText("OCR engine could not read the document.")).toBeDefined();

  // Retry returns to idle.
  await act(async () => {
    fireEvent.click(screen.getByRole("button", { name: "Try Again" }));
  });
  await waitFor(() => expect(screen.getByText("No active processing")).toBeDefined());
});

test("shows submissions from API in the table", async () => {
  mockFetch.mockImplementation((url: string) => {
    if (typeof url === "string" && url.includes("/submissions")) {
      return Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            items: [
              {
                submissionId: "sub-1",
                status: "READY",
                createdAt: "2026-05-24T10:00:00Z",
                fileName: "property-pack.pdf",
              },
            ],
            nextToken: null,
          }),
      });
    }
    return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
  });

  render(<App />);

  await waitFor(() => {
    expect(screen.getByText("property-pack.pdf")).toBeDefined();
  });
  expect(screen.getByText("READY")).toBeDefined();
});

test("renders a partial summary without blanking the page", async () => {
  const summaryResponse = {
    submissionId: "sub-partial",
    status: "NEEDS_REVIEW",
    extracted: null,
    hazards: null,
    aiBrief: null,
    sources: [],
  };

  mockFetch.mockImplementation((url: string, options?: RequestInit) => {
    if (typeof url === "string" && url.includes("/summary")) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve(summaryResponse),
      });
    }
    if (
      typeof url === "string" &&
      url.match(/\/submissions(\?|$)/) &&
      (!options || options.method === "GET")
    ) {
      return Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            items: [
              {
                submissionId: "sub-partial",
                status: "NEEDS_REVIEW",
                createdAt: "2026-05-24T10:00:00Z",
                fileName: "partial-summary.png",
              },
            ],
            nextToken: null,
          }),
      });
    }
    return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
  });

  render(<App />);

  await waitFor(() => {
    expect(screen.getByText("partial-summary.png")).toBeDefined();
  });

  await act(async () => {
    fireEvent.click(
      screen.getByRole("button", {
        name: "Open triage brief for partial-summary.png",
      }),
    );
  });

  await waitFor(() => {
    expect(
      screen.getByText("No extracted facts were saved for this submission."),
    ).toBeDefined();
  });
  expect(screen.getByText("No hazard data was saved for this submission.")).toBeDefined();
  expect(screen.getByText("No AI brief was saved for this submission.")).toBeDefined();
});

test("clear recent submissions empties the local list", async () => {
  mockFetch.mockImplementation((url: string) => {
    if (typeof url === "string" && url.includes("/submissions")) {
      return Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            items: [
              {
                submissionId: "sub-clear",
                status: "READY",
                createdAt: "2026-05-24T10:00:00Z",
                fileName: "clear-me.pdf",
              },
            ],
            nextToken: null,
          }),
      });
    }
    return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
  });

  render(<App />);

  await waitFor(() => {
    expect(screen.getByText("clear-me.pdf")).toBeDefined();
  });

  await act(async () => {
    fireEvent.click(screen.getByRole("button", { name: "Clear" }));
  });

  expect(screen.queryByText("clear-me.pdf")).toBeNull();
  expect(screen.getByText("No submissions yet")).toBeDefined();
});
