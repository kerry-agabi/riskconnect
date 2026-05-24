# RiskLens Token Efficiency Skill

Use this before any multi-file task.

## Rules

- Start with `rg --files`, targeted `rg`, and short reads.
- Read docs by need: product, API, architecture, or standard; avoid loading all docs.
- Prefer one focused implementation slice per task.
- Keep agent handoffs under 15 bullets.
- Avoid restating repo facts already in docs; link to docs instead.
- Do not paste full command outputs unless the output itself is the deliverable.
- Write small diffs and verify locally with the narrowest useful checks.

## Context Budget Pattern

1. Identify touched area.
2. Read one relevant doc and one relevant skill.
3. Inspect existing code in that area.
4. Implement only the requested slice.
5. Report files changed, checks run, and next blocker.

