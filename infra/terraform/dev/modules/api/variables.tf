variable "name_prefix" {
  description = "Resource name prefix."
  type        = string
}

variable "aws_region" {
  description = "AWS region."
  type        = string
}

variable "api_lambda_package_path" {
  description = "Path to the API Lambda zip package."
  type        = string
}

variable "submissions_bucket_arn" {
  description = "Submissions bucket ARN."
  type        = string
}

variable "submissions_bucket_name" {
  description = "Submissions bucket name."
  type        = string
}

variable "processing_queue_arn" {
  description = "Processing queue ARN."
  type        = string
}

variable "processing_queue_url" {
  description = "Processing queue URL."
  type        = string
}

variable "submissions_table_arn" {
  description = "Submission metadata table ARN."
  type        = string
}

variable "submissions_table_name" {
  description = "Submission metadata table name."
  type        = string
}

variable "hazards_table_arn" {
  description = "Hazard cache table ARN."
  type        = string
}

variable "hazards_table_name" {
  description = "Hazard cache table name."
  type        = string
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days."
  type        = number
  default     = 14
}

variable "tags" {
  description = "Common tags."
  type        = map(string)
}

