output "submissions_bucket_name" {
  description = "Submissions bucket name."
  value       = aws_s3_bucket.submissions.bucket
}

output "submissions_bucket_arn" {
  description = "Submissions bucket ARN."
  value       = aws_s3_bucket.submissions.arn
}

output "processing_queue_url" {
  description = "Processing queue URL."
  value       = aws_sqs_queue.processing.url
}

output "processing_queue_arn" {
  description = "Processing queue ARN."
  value       = aws_sqs_queue.processing.arn
}

output "dlq_name" {
  description = "Dead-letter queue name."
  value       = aws_sqs_queue.dlq.name
}

output "worker_lambda_name" {
  description = "Worker Lambda function name."
  value       = aws_lambda_function.worker.function_name
}

output "worker_lambda_arn" {
  description = "Worker Lambda function ARN."
  value       = aws_lambda_function.worker.arn
}

