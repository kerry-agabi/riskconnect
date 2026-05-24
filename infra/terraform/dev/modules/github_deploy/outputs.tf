output "github_deploy_role_arn" {
  description = "Role ARN for GitHub Actions artifact deployment."
  value       = aws_iam_role.github_deploy.arn
}

output "github_oidc_provider_arn" {
  description = "GitHub OIDC provider ARN used by the deploy role."
  value       = local.github_oidc_provider_arn
}

