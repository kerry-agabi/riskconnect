output "web_bucket_name" {
  description = "Frontend S3 bucket name."
  value       = aws_s3_bucket.web.bucket
}

output "web_bucket_arn" {
  description = "Frontend S3 bucket ARN."
  value       = aws_s3_bucket.web.arn
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID."
  value       = aws_cloudfront_distribution.web.id
}

output "cloudfront_distribution_arn" {
  description = "CloudFront distribution ARN."
  value       = aws_cloudfront_distribution.web.arn
}

output "cloudfront_domain_name" {
  description = "CloudFront distribution domain name."
  value       = aws_cloudfront_distribution.web.domain_name
}
