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
- `docs/poc-e2e-implementation-prompts.md`
- `.claude/skills/risklens-aws-standard.md`

Use `STACK_NAME=mrisk`; respect the documented `riskconnect-dev` HCP Terraform workspace and old-role fallback until the migration is complete. Do not deploy or mutate live AWS resources without explicit user confirmation. Prefer Terraform format/init/validate checks and static validation.
