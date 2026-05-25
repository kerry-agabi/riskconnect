# AWS Infrastructure

## Active Terraform Stack

The active AWS infrastructure is Terraform under `infra/terraform`.

- Stack name: `mrisk`
- Dev resource prefix: `riskconnect-dev` while using the old-role fallback; final target is `mrisk-dev`
- Terraform dev root: `infra/terraform/dev`
- Terraform bootstrap root: `infra/terraform/bootstrap`
- HCP Terraform organization: `ka-risklens-mm`
- HCP Terraform workspace: `riskconnect-dev`
- AWS account: `178002661103`
- AWS region: `eu-west-1`
- Auth: Cognito Hosted UI and HTTP API JWT authorizer

The CDK scaffold under `infra/cdk/` is retained only as legacy reference.

## Deployment Model

GitHub Actions packages Lambda artifacts and runs Terraform CLI against HCP Terraform. HCP Terraform performs the remote plan/apply and assumes the AWS run role using workload identity.

After Terraform creates the web bucket and CloudFront distribution, GitHub Actions assumes the separate GitHub OIDC deploy role to upload frontend assets and create a CloudFront invalidation.

No AWS access keys should be stored in GitHub.

## Terraform Roots And Modules

- `infra/terraform/bootstrap`: one-time local bootstrap for the HCP Terraform AWS OIDC provider and run role.
- `infra/terraform/dev`: active dev environment using HCP Terraform remote execution.
- `infra/terraform/dev/modules/api`: API Gateway HTTP API and API Lambda.
- `infra/terraform/dev/modules/processing`: submissions bucket, SQS queue, DLQ, and worker Lambda.
- `infra/terraform/dev/modules/data`: DynamoDB metadata and hazard tables.
- `infra/terraform/dev/modules/web`: private S3 frontend hosting behind CloudFront OAC.
- `infra/terraform/dev/modules/github_deploy`: GitHub Actions OIDC role for frontend artifact deployment.
- `infra/terraform/dev/modules/observability`: budget and CloudWatch alarms.

The dev root keeps modules under `dev/modules/` so HCP Terraform receives them in the uploaded remote-run configuration bundle.

## AWS Services

| Service | Purpose | Budget Notes |
| --- | --- | --- |
| S3 | Static app, raw submissions, results | Low cost for MVP volumes. |
| CloudFront | Fast frontend delivery | Free tier friendly for low traffic. |
| Cognito | Broker login for deployed POC | Hosted UI avoids custom auth UI for MVP. |
| API Gateway HTTP API | Low-latency API | Cheaper than REST API for MVP. |
| Lambda | API handlers and async processing | Pay per request/duration. |
| SQS | Decoupled processing queue and DLQ | Very low cost. |
| DynamoDB on-demand | Status, metadata, hazard cache | No capacity planning. |
| Textract | OCR for PDFs/images | Use page caps to control cost. |
| Bedrock | GenAI extraction and summaries | Use low-cost models and token caps. |
| CloudWatch | Logs, metrics, alarms | Set log retention to 14 days. |
| AWS Budgets | Cost guardrail | Alert before credit exhaustion. |

## Naming And Tags

- Stack name: `mrisk`.
- Dev resource prefix: `riskconnect-dev` while using the old-role fallback; final target is `mrisk-dev`.
- Resource names should follow `mrisk-{env}-{purpose}` when possible.
- Required tags: `Project=mrisk`, `Environment`, `Owner`, `CostCenter=LearningMVP`, `ManagedBy=Terraform`.

Existing HCP names intentionally remain `ka-risklens-mm` / `riskconnect-dev`.

## IAM Principles

- HCP Terraform assumes `riskconnect-dev-tfc-deploy` during the old-role fallback.
- GitHub Actions assumes the Terraform output `github_deploy_role_arn` after apply, for frontend S3 sync and CloudFront invalidation.
- API Lambda can create presigned URLs only for the submissions prefix.
- Worker Lambda can read raw submission objects and write result artifacts.
- Worker Lambda can call Textract and Bedrock only for required actions.
- Avoid wildcard admin policies; scope permissions to required resource ARNs where feasible.

## Runtime Settings

API Lambda:

- Runtime: Python 3.12
- Timeout: 10 seconds
- Memory: 512 MB

Worker Lambda:

- Runtime: Python 3.12
- Timeout: 300 seconds
- Memory: 1024 MB
- Reserved concurrency: unset by default; set a low value only when the AWS account has enough unreserved concurrency headroom

Lambda environment variables must not include AWS-reserved keys such as `AWS_REGION`; Lambda provides those automatically.

## Validation

Use these checks before opening or merging infrastructure changes:

```powershell
terraform fmt -check -recursive infra/terraform
cd infra/terraform/dev
terraform init -backend=false -input=false
terraform validate -no-color
cd ../bootstrap
terraform init -backend=false -input=false
terraform validate -no-color
```

Do not run `terraform apply`, `terraform destroy`, or the `deploy-dev` workflow without explicit approval.
