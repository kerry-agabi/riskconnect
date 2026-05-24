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

