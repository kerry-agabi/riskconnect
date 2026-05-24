variable "name_prefix" {
  description = "Resource name prefix."
  type        = string
}

variable "aws_account_id" {
  description = "AWS account ID."
  type        = string
}

variable "github_owner" {
  description = "GitHub repository owner."
  type        = string
}

variable "github_repo" {
  description = "GitHub repository name."
  type        = string
}

variable "github_environment" {
  description = "GitHub environment used by the deploy workflow."
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

variable "web_bucket_arn" {
  description = "Frontend web bucket ARN."
  type        = string
}

variable "cloudfront_distribution_id" {
  description = "CloudFront distribution ID."
  type        = string
}

variable "tags" {
  description = "Common tags."
  type        = map(string)
}

