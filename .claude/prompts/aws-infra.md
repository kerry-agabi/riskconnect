# Prompt: AWS Infrastructure Slice

Use `aws-infra-lead`.

Task: implement one Terraform module/root or infrastructure concern for RiskLens.

Read:

- `docs/aws-infrastructure.md`
- `docs/poc-e2e-implementation-prompts.md`
- `docs/cost-plan.md`
- `.claude/skills/risklens-aws-standard.md`

Constraints:

- Serverless-first.
- No expensive default services.
- Least-privilege IAM.
- Consistent `mrisk` stack names and tags.
- Keep HCP Terraform workspace `riskconnect-dev` and old-role fallback notes accurate when touching deploy docs.
- Cognito Hosted UI, HTTP API JWT auth, and worker runtime permissions belong in Terraform.
- Budget/log-retention controls.

Run Terraform format/init/validate checks if dependencies are available. Do not apply, destroy, or dispatch deploy workflows without explicit approval.
