# GitHub CI/CD Setup

This guide documents the active CI/CD setup for the RiskLens MVP infrastructure stack.

## Active Defaults

- Stack name: `mrisk`
- GitHub repository: `kerry-agabi/riskconnect`
- HCP Terraform organization: `ka-risklens-mm`
- HCP Terraform workspace: `riskconnect-dev`
- AWS account: `178002661103`
- AWS region: `eu-west-1`

The legacy CDK scaffold is reference only. Active deploys use Terraform and HCP Terraform.

## Branch And Secret Safety

- `main` is the deployable trunk.
- Require pull requests and passing checks before merging.
- Never commit `.env`, AWS access keys, Terraform state, Lambda artifacts, frontend builds, raw submissions, or raw public data dumps.
- Use GitHub secrets for tokens. Do not store tokens in repository variables.

## Required GitHub Configuration

Repository or `dev` environment secret:

- `TFC_API_TOKEN`: HCP Terraform team or user token with access to create runs/configuration versions in `riskconnect-dev`.

Repository variables:

- `STACK_NAME=mrisk`
- `AWS_ACCOUNT_ID=178002661103`
- `AWS_REGION=eu-west-1`
- `APP_ENV=dev`
- `TFC_ORGANIZATION=ka-risklens-mm`
- `TFC_WORKSPACE=riskconnect-dev`

GitHub Actions should not store static AWS keys.

## Required HCP Terraform Workspace Configuration

Set these environment variables in the HCP Terraform workspace `riskconnect-dev`:

- `TFC_AWS_PROVIDER_AUTH=true`
- `TFC_AWS_RUN_ROLE_ARN=arn:aws:iam::178002661103:role/riskconnect-dev-tfc-deploy`

The bootstrap root defaults the HCP Terraform trust subject to `organization:ka-risklens-mm:project:*:workspace:riskconnect-dev:run_phase:*`. If you know the exact HCP Terraform project name, set `tfc_project` to that value; otherwise keep `*`.

The current unblock path reuses the old `riskconnect-dev-tfc-deploy` role while keeping the application stack name `mrisk`. Run bootstrap with `terraform apply -var="project_name=riskconnect"`, then set `TFC_AWS_RUN_ROLE_ARN` to the old role ARN above.

If HCP Terraform assumes `riskconnect-dev-tfc-deploy` but still receives IAM denies for `mrisk-dev-*` roles, the live old-role policy is stale. From `infra/terraform/bootstrap`, apply the emergency inline policy:

```powershell
aws iam put-role-policy `
  --role-name riskconnect-dev-tfc-deploy `
  --policy-name riskconnect-dev-tfc-deploy `
  --policy-document file://riskconnect-dev-tfc-deploy-policy.json
```

The preferred final role after the migration is `arn:aws:iam::178002661103:role/mrisk-dev-tfc-deploy`, but do not switch to it until the bootstrap trust policy has been verified with HCP Terraform.

If the deploy log shows `No valid credential sources found` and `AccessDenied: Not authorized to perform sts:AssumeRoleWithWebIdentity`, the AWS role trust policy does not match the HCP Terraform token. Rerun bootstrap and confirm its `tfc_subject_condition` output matches `organization:ka-risklens-mm:project:*:workspace:riskconnect-dev:run_phase:*` or the exact HCP project name you configured.

During the rename, the run role is allowed to manage both `riskconnect-dev-*` and `mrisk-dev-*` IAM roles. After the migration is complete, remove the unused prefix from `legacy_iam_name_prefixes` in the bootstrap root.

## CI Workflow

`.github/workflows/ci.yml` runs on pull requests and pushes to `main`.

It validates:

- Frontend install, lint, tests, and build.
- Backend install, ruff, mypy, and pytest.
- Docker image builds tagged with the `mrisk` stack name.
- Lambda artifact packaging.
- Terraform format/init/validate for `infra/terraform/dev` and `infra/terraform/bootstrap`.

## Manual Deploy Workflow

`.github/workflows/deploy-dev.yml` is manual-only for MVP cost and safety control.

Deploy flow:

1. Checkout repository.
2. Install Python, Node, and Terraform.
3. Package API and worker Lambda artifacts into `infra/terraform/dev/artifacts/`.
4. Run Terraform CLI against HCP Terraform for stack `mrisk`.
5. Read Terraform outputs for the web bucket, CloudFront distribution, frontend URL, and GitHub deploy role ARN.
6. Assume the GitHub OIDC deploy role.
7. Build and upload the frontend.
8. Invalidate CloudFront.

## Bootstrap

Run once from an admin-capable AWS session:

```powershell
cd infra/terraform/bootstrap
terraform init
terraform apply -var="project_name=riskconnect"
```

The bootstrap output `tfc_run_role_arn` must be copied to HCP Terraform as `TFC_AWS_RUN_ROLE_ARN`.

## Release Checklist

Before running `deploy-dev`:

- CI passes on `main`.
- `STACK_NAME` is `mrisk`.
- HCP Terraform token is a team/user token, not an organization token.
- HCP workspace has `TFC_AWS_PROVIDER_AUTH=true`.
- HCP workspace has the current `riskconnect-dev-tfc-deploy` fallback role ARN, or the verified `mrisk-dev-tfc-deploy` final role ARN.
- AWS budget alert exists.
- Bedrock model access is confirmed if live GenAI processing is enabled.
- No real client data is present in fixtures or artifacts.
- Rollback notes are documented in the pull request or deployment notes.
