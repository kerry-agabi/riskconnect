# Bootstrap

This root creates the AWS IAM OIDC provider and `mrisk` deploy role that HCP Terraform uses for the dev workspace.

Run this once with an admin-capable AWS session. After this bootstrap, normal dev deploys should use HCP Terraform workload identity.

```powershell
terraform init
terraform plan -var="project_name=mrisk"
terraform apply -var="project_name=mrisk"
```

Set the output `tfc_run_role_arn` as the HCP Terraform workspace environment variable `TFC_AWS_RUN_ROLE_ARN`. Also set `TFC_AWS_PROVIDER_AUTH=true`.

If HCP Terraform logs show it assuming `riskconnect-dev-tfc-deploy`, the workspace is still using the old run role. Rerun this bootstrap root, then update `TFC_AWS_RUN_ROLE_ARN` to the `mrisk-dev-tfc-deploy` output before rerunning `deploy-dev`.

The default `legacy_iam_name_prefixes = ["riskconnect-dev"]` lets the new `mrisk` run role clean up old IAM roles during the rename. Remove that legacy prefix after the old resources have been deleted.
