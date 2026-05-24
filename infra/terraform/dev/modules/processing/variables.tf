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

variable "worker_reserved_concurrency" {
  description = "Reserved concurrency for the async worker Lambda."
  type        = number
  default     = 2
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

variable "tags" {
  description = "Common tags."
  type        = map(string)
}

