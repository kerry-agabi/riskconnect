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
