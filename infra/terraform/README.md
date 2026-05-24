# Terraform Layout

Active stack name: `mrisk`.

## Roots

- `bootstrap/`: one-time local bootstrap for the HCP Terraform AWS OIDC provider and `mrisk` run role.
- `dev/`: active dev environment using HCP Terraform remote execution.

## Dev Modules

The `dev/` root keeps its local modules under `dev/modules/` so HCP Terraform
receives them in the uploaded remote-run configuration bundle.

- `api`: Lambda and API Gateway HTTP API.
- `data`: DynamoDB on-demand tables.
- `github_deploy`: GitHub Actions OIDC role for app artifact deployment.
- `observability`: budget and CloudWatch alarms.
- `processing`: submissions bucket, SQS, DLQ, and worker Lambda.
- `web`: private S3 frontend hosting behind CloudFront OAC.

Generated Lambda artifacts are written to `dev/artifacts/` before Terraform runs so HCP Terraform can upload them with the configuration.
