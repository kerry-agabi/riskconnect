import type { AuthStatus } from "../auth/cognito";

interface AuthGateProps {
  status: AuthStatus;
  error: string | null;
  onSignIn: () => void | Promise<void>;
}

/**
 * Quiet, on-brand gate shown while auth is settling or after the sign-in loop
 * has been broken. Stable dimensions to avoid layout shift; no spinner-as-hero.
 */
export function AuthGate({ status, error, onSignIn }: AuthGateProps) {
  const initializing = status === "initializing";

  return (
    <div className="auth-gate" role="status" aria-live="polite">
      <div className="auth-gate-card">
        <p className="auth-gate-eyebrow">RiskLens</p>
        {initializing ? (
          <>
            <h1 className="auth-gate-title">Signing in…</h1>
            <p className="auth-gate-body">
              Verifying your session. This only takes a moment.
            </p>
          </>
        ) : (
          <>
            <h1 className="auth-gate-title">Sign in to continue</h1>
            <p className="auth-gate-body">
              {error ??
                "Your session is not active. Sign in to access the submission workbench."}
            </p>
            <button
              type="button"
              className="auth-gate-button"
              onClick={() => void onSignIn()}
            >
              Sign in
            </button>
          </>
        )}
      </div>
    </div>
  );
}
