# RiskLens Claude Agent Orchestration

## Purpose

Use these project subagents to deliver RiskLens consistently and token-efficiently. Claude Code project subagents live in `.claude/agents/*.md`; this file is the human-readable routing map.

Project skill instructions live in `.claude/skills/`; see `.claude/SKILLS.md` for the short index.

For the exact implementation prompt sequence, use `docs/claude-code-implementation-prompts.md` or `.claude/prompts/implementation-order.md`.

## Agent Roster

| Agent | Use For | Reads First |
| --- | --- | --- |
| `frontend-ui-lead` | React UI, responsive design, Marsh-brand implementation | `docs/README.md`, `.claude/skills/risklens-ui-standard.md` |
| `backend-platform-lead` | Python API, worker, AWS integration boundaries | `docs/api-contract.md`, `.claude/skills/risklens-backend-standard.md` |
| `aws-infra-lead` | Terraform/HCP Terraform, IAM, stack naming, budgets | `docs/aws-infrastructure.md`, `.claude/skills/risklens-aws-standard.md` |
| `genai-workflow-lead` | Bedrock prompts, schemas, token/cost controls | `docs/genai-design.md`, `.claude/skills/risklens-genai-standard.md` |
| `data-enrichment-lead` | FEMA/OpenFEMA/NOAA/Census data ingestion | `docs/data-sources.md` |
| `devops-release-lead` | GitHub Actions, Docker, local/dev deploy flow | `docs/devops.md`, `docs/github-cicd-setup.md` |
| `qa-security-reviewer` | Tests, security, cost, acceptance review | `docs/security-governance.md`, `docs/cost-plan.md` |

## Execution Order

1. Foundation: backend package layout, frontend app shell, config conventions, CI.
2. API and status flow: upload URL, start processing, status polling, summaries.
3. Worker: SQS processing, OCR/text extraction, status events.
4. Data enrichment: geocoding and hazard cache.
5. GenAI: extraction and risk brief prompts with JSON validation.
6. Infrastructure: Terraform modules, HCP Terraform remote runs, budgets, deployment workflow.
7. QA: tests, security review, cost review, demo hardening.

## Delegation Rules

- Delegate narrow tasks with a single acceptance outcome.
- Pass only relevant files and docs, not the whole repository.
- Ask `qa-security-reviewer` for a review before marking a phase complete.
- Keep handoffs under 15 bullets and include exact commands run.
- If a task touches AWS spend or credentials, stop and require explicit user confirmation before deploy or live cloud execution.

## Quality Gates

- Frontend: responsive, accessible, brand-compliant, no overlapping text, no marketing landing page.
- Backend: typed schemas, structured logs, deterministic status transitions, no raw document text in logs.
- Infra: `terraform fmt`, `terraform init -backend=false`, and `terraform validate` pass; least-privilege IAM, budget alarms, no expensive defaults.
- GenAI: schema validation, bounded tokens, evidence-grounded output, no underwriting decisions.
- DevOps: CI covers frontend build, backend lint/tests, Docker build, Lambda packaging, and Terraform validation.
