import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";

// Exercises the redirect re-entrancy guard and the sessionStorage loop breaker.
// The module holds state across calls, so reset modules between tests.

const assignMock = vi.fn();

beforeEach(() => {
  vi.resetModules();
  sessionStorage.clear();
  assignMock.mockReset();
  vi.stubEnv("VITE_COGNITO_DOMAIN", "auth.example.com");
  vi.stubEnv("VITE_COGNITO_CLIENT_ID", "client-123");
  vi.stubEnv("VITE_COGNITO_REDIRECT_URI", "https://app.example.com/");
  Object.defineProperty(window, "location", {
    configurable: true,
    value: {
      assign: assignMock,
      search: "",
      href: "https://app.example.com/",
      origin: "https://app.example.com",
      pathname: "/",
    },
  });
});

afterEach(() => {
  vi.unstubAllEnvs();
});

test("signIn is not re-entrant within a single page load", async () => {
  const { signIn } = await import("./cognito");
  await signIn();
  // Browser navigation is mocked, so redirectInFlight stays set: a second
  // call must be ignored rather than firing another hosted-UI navigation.
  await signIn();
  expect(assignMock).toHaveBeenCalledTimes(1);
});

describe("loop breaker across page loads", () => {
  test("third redirect inside the window trips the breaker", async () => {
    // Simulate the redirect-back cycle: each fresh module load (new page) calls
    // signIn while sessionStorage persists the redirect counter.
    for (let i = 0; i < 2; i += 1) {
      vi.resetModules();
      const mod = await import("./cognito");
      await mod.signIn();
    }
    expect(assignMock).toHaveBeenCalledTimes(2);

    vi.resetModules();
    const mod = await import("./cognito");
    await mod.signIn();
    expect(assignMock).toHaveBeenCalledTimes(2);
    expect(mod.getAuthStatus()).toBe("unauthenticated");
    expect(mod.getAuthError()).toMatch(/multiple attempts/i);
  });
});
