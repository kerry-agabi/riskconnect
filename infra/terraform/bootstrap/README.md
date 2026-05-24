# Bootstrap

This root creates the AWS IAM OIDC provider and deploy role that HCP Terraform uses for the dev workspace.

Run this once with an admin-capable AWS session. After this bootstrap, normal dev deploys should use HCP Terraform workload identity.

```powershell
terraform init
terraform plan
terraform apply
```

Set the output `tfc_run_role_arn` as the HCP Terraform workspace environment variable `TFC_AWS_RUN_ROLE_ARN`. Also set `TFC_AWS_PROVIDER_AUTH=true`.

