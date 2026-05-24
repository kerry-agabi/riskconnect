# Dev Environment

This root provisions the RiskConnect dev environment in `eu-west-1` through HCP Terraform remote execution.

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

