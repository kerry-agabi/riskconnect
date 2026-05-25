variable "aws_account_id" {
  description = "AWS account ID for the personal dev account."
  type        = string
  default     = "178002661103"
}

variable "aws_region" {
  description = "Primary AWS region for the mrisk stack."
  type        = string
  default     = "eu-west-1"
}

variable "project_name" {
  description = "Short project/resource prefix."
  type        = string
  default     = "mrisk"
}

variable "app_env" {
  description = "Environment name."
  type        = string
  default     = "dev"
}

variable "owner" {
  description = "Owner tag value."
  type        = string
  default     = "kerry-agabi"
}

variable "github_owner" {
  description = "GitHub repository owner."
  type        = string
  default     = "kerry-agabi"
}

variable "github_repo" {
  description = "GitHub repository name."
  type        = string
  default     = "riskconnect"
}

variable "github_environment" {
  description = "GitHub environment used by the manual deploy workflow for stack mrisk."
  type        = string
  default     = "dev"
}

variable "create_github_oidc_provider" {
  description = "Create the GitHub OIDC provider. Set false if the account already has one and pass github_oidc_provider_arn."
  type        = bool
  default     = true
}

variable "github_oidc_provider_arn" {
  description = "Existing GitHub OIDC provider ARN when create_github_oidc_provider is false."
  type        = string
  default     = ""
}

variable "api_lambda_package_path" {
  description = "Path to the API Lambda zip package, relative to this root."
  type        = string
  default     = "artifacts/api_lambda.zip"
}

variable "worker_lambda_package_path" {
  description = "Path to the worker Lambda zip package, relative to this root."
  type        = string
  default     = "artifacts/worker_lambda.zip"
}

variable "worker_reserved_concurrency" {
  description = "Optional reserved concurrency for the async worker Lambda. Null leaves concurrency in the account-level unreserved pool."
  type        = number
  default     = null
  nullable    = true
}

variable "monthly_budget_limit_usd" {
  description = "Monthly AWS budget guardrail."
  type        = number
  default     = 50
}

variable "budget_alert_email" {
  description = "Optional email for AWS Budget notifications."
  type        = string
  default     = ""
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

variable "cognito_callback_urls" {
  description = "Allowed Cognito Hosted UI callback URLs."
  type        = list(string)
  default     = ["http://localhost:5173"]
}

variable "cognito_logout_urls" {
  description = "Allowed Cognito Hosted UI logout URLs."
  type        = list(string)
  default     = ["http://localhost:5173"]
}
