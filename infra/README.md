# RiskConnect Infrastructure

This folder contains the active AWS and CI/CD infrastructure path for the RiskConnect dev environment.

## Active Stack

- Terraform root: `infra/terraform/dev`
- HCP Terraform organization: `ka-risklens-mm`
- HCP Terraform workspace: `riskconnect-dev`
- AWS account: `178002661103`
- AWS region: `eu-west-1`

The legacy CDK scaffold remains for historical reference only. New AWS changes should be made in Terraform.

## Deployment Model

GitHub Actions runs the Terraform CLI against HCP Terraform. HCP Terraform performs remote runs and assumes the AWS deploy role through workload identity. GitHub Actions assumes a separate AWS role only to upload frontend assets and invalidate CloudFront after Terraform creates the web bucket and distribution.

No AWS access keys should be stored in GitHub.

## Bootstrap Order

1. Create the private GitHub repository `kerry-agabi/riskconnect`.
2. Run the bootstrap Terraform once from an admin-capable AWS session:

   ```powershell
   cd infra/terraform/bootstrap
   terraform init
   terraform apply
   ```

3. In HCP Terraform workspace `riskconnect-dev`, set:

   - `TFC_AWS_PROVIDER_AUTH=true`
   - `TFC_AWS_RUN_ROLE_ARN=<bootstrap output tfc_run_role_arn>`

4. In GitHub repository settings, set:

   - Secret `TFC_API_TOKEN`
   - Variable `AWS_ACCOUNT_ID=178002661103`
   - Variable `AWS_REGION=eu-west-1`
   - Variable `APP_ENV=dev`
   - Variable `TFC_ORGANIZATION=ka-risklens-mm`
   - Variable `TFC_WORKSPACE=riskconnect-dev`

5. Run the manual `deploy-dev` workflow.

