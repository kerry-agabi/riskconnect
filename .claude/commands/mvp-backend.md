---
description: Implement or review a RiskLens backend/API/worker slice
argument-hint: [backend task]
---

Use the `backend-platform-lead` subagent for this task:

`$ARGUMENTS`

Required context:

- `docs/api-contract.md`
- `docs/architecture.md`
- `docs/poc-e2e-implementation-prompts.md`
- `.claude/skills/risklens-backend-standard.md`
- `.claude/skills/risklens-token-efficiency.md`

Deliver a focused Python implementation with typed schemas, dependency injection seams, structured logging, partial-batch worker semantics, AWS runtime adapters behind service boundaries, and tests.
