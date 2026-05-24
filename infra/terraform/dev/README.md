# Dev Environment

This root provisions the `mrisk` dev environment in `eu-west-1` through HCP Terraform remote execution.

The HCP Terraform workspace remains `riskconnect-dev`; `mrisk` is the stack/resource prefix.

Before running `terraform apply`, generate Lambda artifacts:

```powershell
python ..\..\scripts\package_lambdas.py
```

The GitHub `deploy-dev` workflow does this automatically.

Required HCP Terraform workspace environment variables:

- `TFC_AWS_PROVIDER_AUTH=true`
- `TFC_AWS_RUN_ROLE_ARN=arn:aws:iam::178002661103:role/mrisk-dev-tfc-deploy`

Required GitHub secret:

- `TFC_API_TOKEN`

Required GitHub variable:

- `STACK_NAME=mrisk`
