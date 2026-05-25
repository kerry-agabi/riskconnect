import { renderHook, waitFor, act } from "@testing-library/react";
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import { useSubmissions } from "./useSubmissions";

const mockFetch = vi.fn();

beforeEach(() => {
  global.fetch = mockFetch;
  mockFetch.mockReset();
  mockFetch.mockResolvedValue({
    ok: true,
    json: () => Promise.resolve({ items: [], nextToken: null }),
  });
});

afterEach(() => {
  vi.restoreAllMocks();
});

test("does not fetch while auth is not ready", () => {
  renderHook(() => useSubmissions(false));
  expect(mockFetch).not.toHaveBeenCalled();
});

test("fetches once auth becomes ready", async () => {
  const { rerender } = renderHook(({ ready }) => useSubmissions(ready), {
    initialProps: { ready: false },
  });
  expect(mockFetch).not.toHaveBeenCalled();

  await act(async () => {
    rerender({ ready: true });
  });

  await waitFor(() => {
    expect(mockFetch).toHaveBeenCalledTimes(1);
  });
  expect(mockFetch.mock.calls[0][0]).toContain("/submissions");
});
