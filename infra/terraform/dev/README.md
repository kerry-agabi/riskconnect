# Dev Environment

This root provisions the dev environment in `eu-west-1` through HCP Terraform remote execution.

The HCP Terraform workspace remains `riskconnect-dev`. During the old-role fallback, GitHub Actions passes `project_name=riskconnect` so Terraform manages `riskconnect-dev-*` AWS resources. After the IAM migration is complete, set `TERRAFORM_PROJECT_NAME=mrisk` to use the `mrisk-dev-*` resource prefix.

Before running `terraform apply`, generate Lambda artifacts:

```powershell
python ..\..\scripts\package_lambdas.py
```

The GitHub `deploy-dev` workflow does this automatically.

Required HCP Terraform workspace environment variables:

- `TFC_AWS_PROVIDER_AUTH=true`
- `TFC_AWS_RUN_ROLE_ARN=arn:aws:iam::178002661103:role/riskconnect-dev-tfc-deploy`

Required GitHub secret:

- `TFC_API_TOKEN`

Required GitHub variable:

- `STACK_NAME=mrisk`
- `TERRAFORM_PROJECT_NAME=riskconnect`
