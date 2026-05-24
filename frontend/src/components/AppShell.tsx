import { BrandLogo } from "./BrandLogo";

interface AppShellProps {
  children: React.ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  return (
    <div className="app-shell">
      <header className="app-nav">
        <div className="app-nav-inner">
          <div className="app-nav-brand">
            <BrandLogo />
            <span className="app-nav-divider" aria-hidden="true" />
            <span className="app-nav-title">RiskLens</span>
          </div>
        </div>
      </header>
      <main className="app-content">{children}</main>
    </div>
  );
}
