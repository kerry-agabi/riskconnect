# Bootstrap

This root creates the AWS IAM OIDC provider and deploy role that HCP Terraform uses for the dev workspace.

Run this once with an admin-capable AWS session. After this bootstrap, normal dev deploys should use HCP Terraform workload identity.

```powershell
terraform init
terraform plan
terraform apply
```

Set the output `tfc_run_role_arn` as the HCP Terraform workspace environment variable `TFC_AWS_RUN_ROLE_ARN`. Also set `TFC_AWS_PROVIDER_AUTH=true`.

## Old Role Fallback

To reuse the old `riskconnect-dev-tfc-deploy` role while keeping the application stack name `mrisk`, run bootstrap with the old role prefix:

```powershell
terraform init
terraform plan -var="project_name=riskconnect"
terraform apply -var="project_name=riskconnect"
```

Then set HCP Terraform `TFC_AWS_RUN_ROLE_ARN` to:

```text
arn:aws:iam::178002661103:role/riskconnect-dev-tfc-deploy
```

The default IAM prefix allowlist includes both `riskconnect-dev` and `mrisk-dev`, so the old run role can clean up old resources and manage the new `mrisk` IAM resources.

If bootstrap does not update the live old role policy, apply the checked-in emergency inline policy with an admin-capable AWS session:

```powershell
aws iam put-role-policy `
  --role-name riskconnect-dev-tfc-deploy `
  --policy-name riskconnect-dev-tfc-deploy `
  --policy-document file://riskconnect-dev-tfc-deploy-policy.json
```

This policy is the same compatibility scope as the Terraform bootstrap policy: it lets the old HCP Terraform run role clean up `riskconnect-dev-*` IAM resources and create/manage `mrisk-dev-*` IAM resources.

The default HCP Terraform trust subject is `organization:ka-risklens-mm:project:*:workspace:riskconnect-dev:run_phase:*`. If you know the exact HCP Terraform project name, set `tfc_project` to that value; otherwise keep `*` so the role trust policy matches the existing workspace even if it is not in a project named `riskconnect`.

If HCP Terraform logs show it assuming `riskconnect-dev-tfc-deploy`, that is expected while using the old-role fallback. If you later move to the final `mrisk-dev-tfc-deploy` role, rerun bootstrap with the default `project_name=mrisk`, then update `TFC_AWS_RUN_ROLE_ARN` to the new output before rerunning `deploy-dev`.

If HCP Terraform reports `No valid credential sources found` with `AccessDenied: Not authorized to perform sts:AssumeRoleWithWebIdentity`, rerun bootstrap and confirm the `tfc_subject_condition` output matches the HCP workspace:

```text
organization:ka-risklens-mm:project:*:workspace:riskconnect-dev:run_phase:*
```

The default `legacy_iam_name_prefixes = ["riskconnect-dev", "mrisk-dev"]` lets either run-role name work during the rename. Remove the unused prefix after the migration is complete.
