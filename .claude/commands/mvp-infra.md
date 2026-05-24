---
description: Implement or review RiskLens AWS infrastructure and CI/CD
argument-hint: [infra task]
---

Use the `aws-infra-lead` or `devops-release-lead` subagent based on the task:

`$ARGUMENTS`

Required context:

- `docs/aws-infrastructure.md`
- `docs/cost-plan.md`
- `docs/github-cicd-setup.md`
- `.claude/skills/risklens-aws-standard.md`

Do not deploy or mutate live AWS resources without explicit user confirmation. Prefer `cdk synth` and static validation.

