import { BrandLogo } from "./BrandLogo";

interface AppShellProps {
  children: React.ReactNode;
  onSignOut?: () => void;
}

export function AppShell({ children, onSignOut }: AppShellProps) {
  return (
    <div className="app-shell">
      <header className="app-nav">
        <div className="app-nav-inner">
          <div className="app-nav-brand">
            <BrandLogo />
            <span className="app-nav-divider" aria-hidden="true" />
            <span className="app-nav-title">RiskLens</span>
          </div>
          {onSignOut && (
            <div className="app-nav-actions">
              <button
                type="button"
                className="app-nav-button"
                onClick={onSignOut}
              >
                Log out
              </button>
            </div>
          )}
        </div>
      </header>
      <main className="app-content">{children}</main>
    </div>
  );
}
