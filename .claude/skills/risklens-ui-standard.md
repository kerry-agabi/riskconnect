# RiskLens UI Standard

## Brand

- Use the approved Marsh logo asset only from `frontend/src/assets/brand/marsh-logo.svg` or `.png`.
- If no approved asset exists, use a text fallback in `BrandLogo` and mark final logo integration as blocked.
- Do not scrape, redraw, trace, recolor, or approximate the Marsh logo.

## Visual System

- Tone: enterprise insurance workflow, quiet, dense, trustworthy.
- Palette: midnight/deep blue base, restrained cyan/teal accents, neutral greys, white surfaces.
- Avoid purple-heavy gradients, beige/brown themes, decorative blobs, oversized marketing heroes, and generic AI-chat styling.
- Border radius: 8px or less unless a component needs circular icon buttons.
- Typography: system or licensed enterprise sans-serif; no viewport-scaled type.

## Layout

- First screen is the actual workbench: upload/status/queue summary, not a landing page.
- Use full-width app shell with top nav, left/right contextual panels only when useful.
- Cards are for repeated items or focused panels only; do not nest cards.
- Tables, status steps, upload zones, and result panels need stable dimensions.
- Mobile layout must preserve all core actions without overlap.

## Interaction

- Use icons for common actions when an icon library is available.
- Show upload progress and backend status separately.
- `READY`, `NEEDS_REVIEW`, and `FAILED` need distinct visual treatments.
- Display AI output as a draft requiring broker review.

## Acceptance

- No text overflow at mobile width.
- Keyboard-accessible upload and actions.
- Contrast meets WCAG AA for normal text.
- The interface looks like a professional internal insurance tool.

