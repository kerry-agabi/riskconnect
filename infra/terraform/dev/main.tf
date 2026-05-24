locals {
  name_prefix = "${var.project_name}-${var.app_env}"

  tags = {
    Project     = "mrisk"
    Environment = var.app_env
    Owner       = var.owner
    CostCenter  = "LearningMVP"
    ManagedBy   = "Terraform"
  }

  api_lambda_package_path    = abspath("${path.module}/${var.api_lambda_package_path}")
  worker_lambda_package_path = abspath("${path.module}/${var.worker_lambda_package_path}")
}

module "data" {
  source = "./modules/data"

  name_prefix = local.name_prefix
  tags        = local.tags
}

module "processing" {
  source = "./modules/processing"

  name_prefix                 = local.name_prefix
  aws_account_id              = var.aws_account_id
  aws_region                  = var.aws_region
  worker_lambda_package_path  = local.worker_lambda_package_path
  worker_reserved_concurrency = var.worker_reserved_concurrency
  log_retention_days          = var.log_retention_days
  force_destroy_buckets       = var.force_destroy_buckets
  tags                        = local.tags
}

module "api" {
  source = "./modules/api"

  name_prefix             = local.name_prefix
  aws_region              = var.aws_region
  api_lambda_package_path = local.api_lambda_package_path
  log_retention_days      = var.log_retention_days

  submissions_bucket_arn  = module.processing.submissions_bucket_arn
  submissions_bucket_name = module.processing.submissions_bucket_name
  processing_queue_arn    = module.processing.processing_queue_arn
  processing_queue_url    = module.processing.processing_queue_url

  submissions_table_arn  = module.data.submissions_table_arn
  submissions_table_name = module.data.submissions_table_name
  hazards_table_arn      = module.data.hazards_table_arn
  hazards_table_name     = module.data.hazards_table_name

  tags = local.tags
}

module "web" {
  source = "./modules/web"

  name_prefix           = local.name_prefix
  aws_account_id        = var.aws_account_id
  aws_region            = var.aws_region
  api_domain_name       = module.api.api_domain_name
  force_destroy_buckets = var.force_destroy_buckets
  tags                  = local.tags
}

module "github_deploy" {
  source = "./modules/github_deploy"

  name_prefix                 = local.name_prefix
  aws_account_id              = var.aws_account_id
  github_owner                = var.github_owner
  github_repo                 = var.github_repo
  github_environment          = var.github_environment
  create_github_oidc_provider = var.create_github_oidc_provider
  github_oidc_provider_arn    = var.github_oidc_provider_arn
  web_bucket_arn              = module.web.web_bucket_arn
  cloudfront_distribution_id  = module.web.cloudfront_distribution_id
  tags                        = local.tags
}

module "observability" {
  source = "./modules/observability"

  name_prefix              = local.name_prefix
  monthly_budget_limit_usd = var.monthly_budget_limit_usd
  budget_alert_email       = var.budget_alert_email
  api_lambda_name          = module.api.api_lambda_name
  worker_lambda_name       = module.processing.worker_lambda_name
  dlq_name                 = module.processing.dlq_name
  tags                     = local.tags
}
