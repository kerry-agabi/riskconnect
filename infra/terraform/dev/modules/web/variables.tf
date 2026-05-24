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

variable "api_domain_name" {
  description = "API Gateway domain name without the https scheme."
  type        = string
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

