variable "aws_account_id" {
  description = "AWS account ID for the personal dev account."
  type        = string
  default     = "178002661103"
}

variable "aws_region" {
  description = "Primary AWS region for RiskConnect."
  type        = string
  default     = "eu-west-1"
}

variable "project_name" {
  description = "Short project name used in IAM names and tags."
  type        = string
  default     = "riskconnect"
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

variable "tfc_organization" {
  description = "HCP Terraform organization."
  type        = string
  default     = "ka-risklens-mm"
}

variable "tfc_project" {
  description = "HCP Terraform project name in workload identity subject matching. Use * when the project name is not fixed yet."
  type        = string
  default     = "riskconnect"
}

variable "tfc_workspace" {
  description = "HCP Terraform workspace that will run the dev stack."
  type        = string
  default     = "riskconnect-dev"
}

variable "aws_profile" {

  description = "AWS CLI profile name to use for authentication. Ensure this profile has the necessary permissions to manage AWS resources for the project."
  type        = string
  default     = "kerry-agabi"
}

