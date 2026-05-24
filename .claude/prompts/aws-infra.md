# Prompt: AWS Infrastructure Slice

Use `aws-infra-lead`.

Task: implement one CDK stack or infrastructure concern for RiskLens.

Read:

- `docs/aws-infrastructure.md`
- `docs/cost-plan.md`
- `.claude/skills/risklens-aws-standard.md`

Constraints:

- Serverless-first.
- No expensive default services.
- Least-privilege IAM.
- Consistent names and tags.
- Budget/log-retention controls.

Run `cdk synth` if dependencies are available. Do not deploy without explicit approval.

