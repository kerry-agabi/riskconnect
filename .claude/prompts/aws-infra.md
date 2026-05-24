# Prompt: AWS Infrastructure Slice

Use `aws-infra-lead`.

Task: implement one Terraform module/root or infrastructure concern for RiskLens.

Read:

- `docs/aws-infrastructure.md`
- `docs/cost-plan.md`
- `.claude/skills/risklens-aws-standard.md`

Constraints:

- Serverless-first.
- No expensive default services.
- Least-privilege IAM.
- Consistent `mrisk` stack names and tags.
- Budget/log-retention controls.

Run Terraform format/init/validate checks if dependencies are available. Do not apply, destroy, or dispatch deploy workflows without explicit approval.
