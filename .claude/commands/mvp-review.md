---
description: Run strict RiskLens QA, security, cost, and acceptance review
argument-hint: [changed files or phase]
---

Use the `qa-security-reviewer` subagent to review:

`$ARGUMENTS`

Focus on bugs, contract drift, missing tests, data/privacy exposure, Cognito and worker retry behavior, GenAI governance, AWS cost risk, `mrisk` deploy drift, and frontend polish gaps. Findings first, ordered by severity, with file references where possible.
