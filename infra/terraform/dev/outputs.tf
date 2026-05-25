output "api_endpoint" {
  description = "Direct API Gateway endpoint."
  value       = module.api.api_endpoint
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID for invalidations."
  value       = module.web.cloudfront_distribution_id
}

output "cloudfront_domain_name" {
  description = "CloudFront domain for the dev frontend."
  value       = module.web.cloudfront_domain_name
}

output "frontend_url" {
  description = "Default frontend URL."
  value       = "https://${module.web.cloudfront_domain_name}"
}

output "web_bucket_name" {
  description = "Frontend deployment bucket."
  value       = module.web.web_bucket_name
}

output "submissions_bucket_name" {
  description = "Submission upload bucket."
  value       = module.processing.submissions_bucket_name
}

output "processing_queue_url" {
  description = "SQS processing queue URL."
  value       = module.processing.processing_queue_url
}

output "api_lambda_name" {
  description = "API Lambda function name."
  value       = module.api.api_lambda_name
}

output "worker_lambda_name" {
  description = "Worker Lambda function name."
  value       = module.processing.worker_lambda_name
}

output "submissions_table_name" {
  description = "Submission metadata table name."
  value       = module.data.submissions_table_name
}

output "hazards_table_name" {
  description = "Hazard cache table name."
  value       = module.data.hazards_table_name
}

output "github_deploy_role_arn" {
  description = "Set or use this role for GitHub Actions artifact deployment."
  value       = module.github_deploy.github_deploy_role_arn
}

output "cognito_user_pool_id" {
  description = "Cognito user pool ID for broker login."
  value       = module.api.cognito_user_pool_id
}

output "cognito_user_pool_client_id" {
  description = "Cognito app client ID for frontend login."
  value       = module.api.cognito_user_pool_client_id
}

output "cognito_domain" {
  description = "Cognito Hosted UI domain."
  value       = module.api.cognito_domain
}

output "budget_name" {
  description = "AWS Budget name."
  value       = module.observability.budget_name
}
