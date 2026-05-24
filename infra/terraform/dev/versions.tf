terraform {
  required_version = ">= 1.7.0"

  cloud {
    organization = "ka-risklens-mm"

    workspaces {
      name = "riskconnect-dev"
    }
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.90"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = local.tags
  }
}

