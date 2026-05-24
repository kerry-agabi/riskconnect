// TODO: Replace text fallback with approved logo asset from src/assets/brand/marsh-logo.svg
// The approved Marsh logo asset is required before final polish.
// Do NOT scrape, redraw, trace, or approximate the official Marsh logo.

let logoUrl: string | null = null;

try {
  // Attempt to import the approved logo asset at build time via Vite's static import.
  // This will be replaced by the actual asset URL if the file exists.
  const mod = import.meta.glob("../assets/brand/marsh-logo.{svg,png}", {
    eager: true,
    import: "default",
  });
  const keys = Object.keys(mod);
  if (keys.length > 0) {
    logoUrl = mod[keys[0]] as string;
  }
} catch {
  // Asset not available; text fallback will be used.
}

export function BrandLogo() {
  if (logoUrl) {
    return (
      <img
        src={logoUrl}
        alt="Marsh"
        className="brand-logo-img"
        height={28}
      />
    );
  }

  return (
    <span className="brand-logo-text" aria-label="Marsh">
      MARSH
    </span>
  );
}
