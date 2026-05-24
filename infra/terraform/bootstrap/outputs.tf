output "tfc_oidc_provider_arn" {
  description = "AWS IAM OIDC provider ARN for HCP Terraform."
  value       = aws_iam_openid_connect_provider.tfc.arn
}

output "tfc_run_role_arn" {
  description = "Set this as TFC_AWS_RUN_ROLE_ARN in the riskconnect-dev HCP Terraform workspace. Old-role fallback uses riskconnect-dev-tfc-deploy."
  value       = aws_iam_role.tfc_deploy.arn
}

output "tfc_subject_condition" {
  description = "Workload identity subject allowed to assume the HCP Terraform role."
  value       = local.tfc_subject
}
