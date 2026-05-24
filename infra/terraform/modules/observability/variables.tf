variable "name_prefix" {
  description = "Resource name prefix."
  type        = string
}

variable "monthly_budget_limit_usd" {
  description = "Monthly AWS budget limit in USD."
  type        = number
  default     = 50
}

variable "budget_alert_email" {
  description = "Optional email for AWS Budget notifications."
  type        = string
  default     = ""
}

variable "api_lambda_name" {
  description = "API Lambda function name."
  type        = string
}

variable "worker_lambda_name" {
  description = "Worker Lambda function name."
  type        = string
}

variable "dlq_name" {
  description = "Dead-letter queue name."
  type        = string
}

variable "tags" {
  description = "Common tags."
  type        = map(string)
}

