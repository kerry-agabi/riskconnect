import { setAuthTokenProvider, setUnauthorizedHandler } from "../api/client";

interface CognitoConfig {
  domain: string;
  clientId: string;
  redirectUri: string;
  logoutUri: string;
}

interface StoredTokens {
  accessToken: string;
  idToken?: string;
  refreshToken?: string;
  expiresAt: number;
}

interface TokenResponse {
  access_token: string;
  id_token?: string;
  refresh_token?: string;
  expires_in: number;
  token_type: string;
}

const TOKEN_KEY = "risklens.cognito.tokens";
const PKCE_VERIFIER_KEY = "risklens.cognito.pkceVerifier";
const OAUTH_STATE_KEY = "risklens.cognito.state";
const REDIRECT_LOG_KEY = "risklens.cognito.redirects";
const TOKEN_REFRESH_SKEW_MS = 60_000;
const AUTH_SCOPE = "openid email profile";

// Loop breaker: if more than MAX redirects happen inside WINDOW, stop bouncing
// and surface an error so the user sees a manual Sign-in CTA instead of a storm.
const REDIRECT_WINDOW_MS = 20_000;
const REDIRECT_MAX = 2;

/**
 * Auth readiness signal. API calls must wait for this to settle so requests
 * never go out before the code-for-token exchange has completed.
 *   initializing   - bootstrap in progress (exchange / token read pending)
 *   authenticated  - a usable token exists (or auth is not configured for dev)
 *   unauthenticated - no token, loop broken, or session expired
 */
export type AuthStatus = "initializing" | "authenticated" | "unauthenticated";

let authStatus: AuthStatus = "initializing";
let authError: string | null = null;
const statusListeners = new Set<(status: AuthStatus) => void>();

// Re-entrancy guard so a 401 storm or concurrent callers cannot fire multiple
// hosted-UI navigations.
let redirectInFlight = false;

export function getAuthStatus(): AuthStatus {
  return authStatus;
}

export function getAuthError(): string | null {
  return authError;
}

export function onAuthStatusChange(
  cb: (status: AuthStatus) => void,
): () => void {
  statusListeners.add(cb);
  return () => {
    statusListeners.delete(cb);
  };
}

function setAuthStatus(next: AuthStatus, error: string | null = null): void {
  authError = error;
  if (authStatus === next) return;
  authStatus = next;
  statusListeners.forEach((cb) => cb(next));
}

function getConfig(): CognitoConfig | null {
  const domain = import.meta.env.VITE_COGNITO_DOMAIN;
  const clientId = import.meta.env.VITE_COGNITO_CLIENT_ID;
  if (!domain || !clientId) return null;

  const defaultUri = window.location.origin + window.location.pathname;
  return {
    domain: domain.replace(/^https?:\/\//, "").replace(/\/$/, ""),
    clientId,
    redirectUri: import.meta.env.VITE_COGNITO_REDIRECT_URI || defaultUri,
    logoutUri: import.meta.env.VITE_COGNITO_LOGOUT_URI || defaultUri,
  };
}

function readTokens(): StoredTokens | null {
  const raw = sessionStorage.getItem(TOKEN_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as StoredTokens;
  } catch {
    sessionStorage.removeItem(TOKEN_KEY);
    return null;
  }
}

function writeTokens(response: TokenResponse): void {
  const current = readTokens();
  const tokens: StoredTokens = {
    accessToken: response.access_token,
    idToken: response.id_token,
    refreshToken: response.refresh_token || current?.refreshToken,
    expiresAt: Date.now() + response.expires_in * 1000,
  };
  sessionStorage.setItem(TOKEN_KEY, JSON.stringify(tokens));
}

function clearAuthState(): void {
  sessionStorage.removeItem(TOKEN_KEY);
  sessionStorage.removeItem(PKCE_VERIFIER_KEY);
  sessionStorage.removeItem(OAUTH_STATE_KEY);
}

/**
 * Records a redirect timestamp and reports whether the loop-breaker threshold
 * has been exceeded within the rolling window. When tripped we must not
 * redirect again until a successful token acquisition resets the counter.
 */
function recordRedirectAndCheckLoop(): boolean {
  const now = Date.now();
  let timestamps: number[] = [];
  try {
    const raw = sessionStorage.getItem(REDIRECT_LOG_KEY);
    if (raw) timestamps = JSON.parse(raw) as number[];
  } catch {
    timestamps = [];
  }
  timestamps = timestamps.filter((t) => now - t < REDIRECT_WINDOW_MS);
  timestamps.push(now);
  sessionStorage.setItem(REDIRECT_LOG_KEY, JSON.stringify(timestamps));
  return timestamps.length > REDIRECT_MAX;
}

function resetRedirectLoop(): void {
  sessionStorage.removeItem(REDIRECT_LOG_KEY);
}

function randomString(byteLength = 32): string {
  const bytes = new Uint8Array(byteLength);
  crypto.getRandomValues(bytes);
  return base64Url(bytes);
}

function base64Url(bytes: Uint8Array): string {
  let binary = "";
  bytes.forEach((byte) => {
    binary += String.fromCharCode(byte);
  });
  return btoa(binary)
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/, "");
}

async function sha256Base64Url(value: string): Promise<string> {
  const encoded = new TextEncoder().encode(value);
  const digest = await crypto.subtle.digest("SHA-256", encoded);
  return base64Url(new Uint8Array(digest));
}

function tokenEndpoint(config: CognitoConfig): string {
  return `https://${config.domain}/oauth2/token`;
}

async function postTokenRequest(
  config: CognitoConfig,
  body: URLSearchParams,
): Promise<TokenResponse> {
  const response = await fetch(tokenEndpoint(config), {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
  if (!response.ok) {
    clearAuthState();
    throw new Error(`Cognito token request failed with status ${response.status}`);
  }
  return response.json() as Promise<TokenResponse>;
}

async function refresh(config: CognitoConfig, refreshToken: string): Promise<string | null> {
  const body = new URLSearchParams({
    grant_type: "refresh_token",
    client_id: config.clientId,
    refresh_token: refreshToken,
  });
  const response = await postTokenRequest(config, body);
  writeTokens(response);
  // API Gateway JWT authorizer validates `aud` (= app client id), which only
  // the ID token carries; access tokens expose `client_id` instead. Send the
  // ID token, falling back to the access token if one is somehow absent.
  return response.id_token ?? response.access_token;
}

export async function signIn(): Promise<void> {
  const config = getConfig();
  if (!config) return;

  // Re-entrancy guard: a single redirect at a time.
  if (redirectInFlight) return;

  // Loop breaker: too many redirects in the window means the round-trip keeps
  // failing (e.g. authorizer rejects every fresh token). Stop and surface it.
  if (recordRedirectAndCheckLoop()) {
    setAuthStatus(
      "unauthenticated",
      "Sign-in did not complete after multiple attempts. Please sign in again.",
    );
    return;
  }

  redirectInFlight = true;

  const verifier = randomString(64);
  const state = randomString(32);
  const challenge = await sha256Base64Url(verifier);
  sessionStorage.setItem(PKCE_VERIFIER_KEY, verifier);
  sessionStorage.setItem(OAUTH_STATE_KEY, state);

  const params = new URLSearchParams({
    client_id: config.clientId,
    code_challenge: challenge,
    code_challenge_method: "S256",
    redirect_uri: config.redirectUri,
    response_type: "code",
    scope: AUTH_SCOPE,
    state,
  });

  window.location.assign(`https://${config.domain}/oauth2/authorize?${params}`);
}

export function signOut(): void {
  const config = getConfig();
  clearAuthState();
  if (!config) return;
  const params = new URLSearchParams({
    client_id: config.clientId,
    logout_uri: config.logoutUri,
  });
  window.location.assign(`https://${config.domain}/logout?${params}`);
}

async function completeSignInFromUrl(config: CognitoConfig): Promise<boolean> {
  const params = new URLSearchParams(window.location.search);
  const code = params.get("code");
  const state = params.get("state");
  if (!code) return false;

  const expectedState = sessionStorage.getItem(OAUTH_STATE_KEY);
  const verifier = sessionStorage.getItem(PKCE_VERIFIER_KEY);
  if (!state || state !== expectedState || !verifier) {
    clearAuthState();
    await signIn();
    return true;
  }

  const body = new URLSearchParams({
    grant_type: "authorization_code",
    client_id: config.clientId,
    code,
    code_verifier: verifier,
    redirect_uri: config.redirectUri,
  });
  const response = await postTokenRequest(config, body);
  writeTokens(response);
  sessionStorage.removeItem(PKCE_VERIFIER_KEY);
  sessionStorage.removeItem(OAUTH_STATE_KEY);

  const cleanUrl = new URL(window.location.href);
  cleanUrl.searchParams.delete("code");
  cleanUrl.searchParams.delete("state");
  window.history.replaceState({}, document.title, cleanUrl.toString());
  return true;
}

async function getAccessToken(): Promise<string | null> {
  const config = getConfig();
  if (!config) return null;

  const tokens = readTokens();
  if (!tokens) {
    // Never redirect as a side effect of a data fetch. Redirects are owned by
    // the auth bootstrap and the guarded unauthorized handler.
    return null;
  }

  if (tokens.expiresAt - Date.now() > TOKEN_REFRESH_SKEW_MS) {
    // Authorizer validates the `aud` claim (ID token only); fall back to the
    // access token only if no ID token was stored.
    return tokens.idToken ?? tokens.accessToken;
  }

  if (tokens.refreshToken) {
    try {
      return await refresh(config, tokens.refreshToken);
    } catch {
      // Refresh failed (e.g. expired refresh token). Report unusable; the
      // unauthorized handler / bootstrap decides whether to redirect.
      return null;
    }
  }

  return null;
}

export async function installCognitoAuth(): Promise<void> {
  const config = getConfig();
  if (!config) {
    // Auth not configured (local/dev/test): requests go out unauthenticated,
    // so there is nothing to gate on. Treat as ready immediately.
    setAuthStatus("authenticated");
    return;
  }

  setAuthTokenProvider(getAccessToken);
  setUnauthorizedHandler(async () => {
    // A 401 while we believe we are authenticated means the token is being
    // rejected. Do not auto-loop: drop to unauthenticated and let the UI show
    // a manual Sign-in CTA. Only the explicit CTA re-enters signIn().
    if (authStatus === "authenticated") {
      clearAuthState();
      setAuthStatus(
        "unauthenticated",
        "Your session was rejected. Please sign in again.",
      );
      return;
    }
    // Otherwise (already initializing/unauthenticated) attempt a guarded,
    // loop-broken redirect.
    clearAuthState();
    await signIn();
  });

  try {
    // Resolve status only AFTER the code-for-token exchange and token read.
    const completed = await completeSignInFromUrl(config);
    const token = await getAccessToken();
    if (token) {
      // Successful acquisition clears the redirect-loop counter.
      resetRedirectLoop();
      setAuthStatus("authenticated");
      return;
    }
    if (completed) {
      // Exchange ran but produced no usable token.
      setAuthStatus("unauthenticated", "Sign-in did not return a valid session.");
      return;
    }
    // No tokens yet and no callback in the URL: start a guarded sign-in.
    await signIn();
    // If signIn tripped the loop breaker it already set unauthenticated;
    // otherwise the browser is navigating away and status stays initializing.
  } catch (err) {
    setAuthStatus(
      "unauthenticated",
      err instanceof Error ? err.message : "Sign-in failed.",
    );
  }
}
