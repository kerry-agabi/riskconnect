output "submissions_table_name" {
  description = "Submission metadata table name."
  value       = aws_dynamodb_table.submissions.name
}

output "submissions_table_arn" {
  description = "Submission metadata table ARN."
  value       = aws_dynamodb_table.submissions.arn
}

output "hazards_table_name" {
  description = "Hazard cache table name."
  value       = aws_dynamodb_table.hazards.name
}

output "hazards_table_arn" {
  description = "Hazard cache table ARN."
  value       = aws_dynamodb_table.hazards.arn
}

