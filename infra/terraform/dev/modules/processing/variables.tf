variable "name_prefix" {
  description = "Resource name prefix."
  type        = string
}

variable "aws_account_id" {
  description = "AWS account ID."
  type        = string
}

variable "aws_region" {
  description = "AWS region."
  type        = string
}

variable "worker_lambda_package_path" {
  description = "Path to the worker Lambda zip package."
  type        = string
}

variable "submissions_table_name" {
  description = "DynamoDB submissions table name."
  type        = string
}

variable "submissions_table_arn" {
  description = "DynamoDB submissions table ARN."
  type        = string
}

variable "hazards_table_name" {
  description = "DynamoDB hazards table name."
  type        = string
}

variable "hazards_table_arn" {
  description = "DynamoDB hazards table ARN."
  type        = string
}

variable "worker_reserved_concurrency" {
  description = "Optional reserved concurrency for the async worker Lambda. Null leaves concurrency in the account-level unreserved pool."
  type        = number
  default     = null
  nullable    = true
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days."
  type        = number
  default     = 14
}

variable "force_destroy_buckets" {
  description = "Allow Terraform to delete non-empty dev buckets."
  type        = bool
  default     = false
}

variable "submissions_cors_allowed_origins" {
  description = "Browser origins allowed to PUT directly to presigned submission upload URLs."
  type        = list(string)
  default     = ["*"]
}

variable "tags" {
  description = "Common tags."
  type        = map(string)
}
