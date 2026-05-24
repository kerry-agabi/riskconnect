# RiskLens AWS Standard

## Naming

- Stack names: `risklens-{env}-{component}`.
- Resource names: `risklens-{env}-{purpose}` where global uniqueness permits.
- Tags: `Project=RiskLens`, `Environment`, `Owner`, `CostCenter=LearningMVP`.

## Cost Constraints

- Default to S3, CloudFront, API Gateway HTTP API, Lambda, SQS, DynamoDB on-demand, Textract, Bedrock, CloudWatch, Budgets.
- Do not add EKS, NAT Gateway, RDS, OpenSearch, provisioned Bedrock, or always-on EC2 by default.
- Set worker reserved concurrency low for MVP.
- Set CloudWatch retention to 14 days.

## Security

- Block public S3 access except CloudFront web delivery pattern.
- Use encryption at rest.
- Scope IAM to prefixes and specific actions.
- Use GitHub OIDC for CI/CD deploy role.
- Never store AWS access keys in repo or workflow secrets unless explicitly approved as a temporary fallback.

## Deployment

- `cdk synth` is safe for routine validation.
- `cdk bootstrap`, `cdk deploy`, and `cdk destroy` require explicit user confirmation.
- Manual deploy workflow only for MVP.

