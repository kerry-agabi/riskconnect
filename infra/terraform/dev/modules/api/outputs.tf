output "api_endpoint" {
  description = "API Gateway HTTP API endpoint."
  value       = aws_apigatewayv2_api.api.api_endpoint
}

output "api_domain_name" {
  description = "API Gateway domain name without scheme for CloudFront origin."
  value       = replace(aws_apigatewayv2_api.api.api_endpoint, "https://", "")
}

output "api_lambda_name" {
  description = "API Lambda function name."
  value       = aws_lambda_function.api.function_name
}

output "api_lambda_arn" {
  description = "API Lambda function ARN."
  value       = aws_lambda_function.api.arn
}

output "cognito_user_pool_id" {
  description = "Cognito user pool ID for broker login."
  value       = aws_cognito_user_pool.broker.id
}

output "cognito_user_pool_client_id" {
  description = "Cognito app client ID for the frontend."
  value       = aws_cognito_user_pool_client.frontend.id
}

output "cognito_domain" {
  description = "Cognito Hosted UI domain."
  value       = "${aws_cognito_user_pool_domain.frontend.domain}.auth.${var.aws_region}.amazoncognito.com"
}
