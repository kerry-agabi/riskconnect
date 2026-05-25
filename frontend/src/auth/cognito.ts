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
const TOKEN_REFRESH_SKEW_MS = 60_000;
const AUTH_SCOPE = "openid email profile";

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
  return response.access_token;
}

export async function signIn(): Promise<void> {
  const config = getConfig();
  if (!config) return;

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
    await signIn();
    return null;
  }

  if (tokens.expiresAt - Date.now() > TOKEN_REFRESH_SKEW_MS) {
    return tokens.accessToken;
  }

  if (tokens.refreshToken) {
    return refresh(config, tokens.refreshToken);
  }

  await signIn();
  return null;
}

export async function installCognitoAuth(): Promise<void> {
  const config = getConfig();
  if (!config) return;

  setAuthTokenProvider(getAccessToken);
  setUnauthorizedHandler(async () => {
    clearAuthState();
    await signIn();
  });

  const completed = await completeSignInFromUrl(config);
  if (!completed && !readTokens()) {
    await signIn();
  }
}
