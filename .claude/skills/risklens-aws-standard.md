# RiskLens AWS Standard

## Naming

- Stack name: `mrisk`.
- Resource names: `mrisk-{env}-{purpose}` where global uniqueness permits.
- Tags: `Project=mrisk`, `Environment`, `Owner`, `CostCenter=LearningMVP`, `ManagedBy=Terraform`.

## Cost Constraints

- Default to S3, CloudFront, API Gateway HTTP API, Lambda, SQS, DynamoDB on-demand, Textract, Bedrock, CloudWatch, Budgets.
- Do not add EKS, NAT Gateway, RDS, OpenSearch, provisioned Bedrock, or always-on EC2 by default.
- Leave worker reserved concurrency unset by default; only reserve concurrency when the AWS account has enough unreserved headroom.
- Set CloudWatch retention to 14 days.

## Security

- Block public S3 access except CloudFront web delivery pattern.
- Use encryption at rest.
- Scope IAM to prefixes and specific actions.
- Use HCP Terraform workload identity for Terraform applies and GitHub OIDC for frontend artifact deployment.
- Never store AWS access keys in repo or workflow secrets unless explicitly approved as a temporary fallback.

## Deployment

- `terraform fmt`, `terraform init -backend=false`, and `terraform validate` are safe for routine validation.
- `terraform apply`, `terraform destroy`, bootstrap changes, and deploy workflow dispatch require explicit user confirmation.
- Manual deploy workflow only for MVP.
