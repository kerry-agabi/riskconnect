locals {
  name_prefix = "${var.project_name}-${var.app_env}"
  managed_iam_name_prefixes = distinct(concat(
    [local.name_prefix],
    var.legacy_iam_name_prefixes,
  ))

  managed_iam_policy_arns = [
    for prefix in local.managed_iam_name_prefixes :
    "arn:aws:iam::${var.aws_account_id}:policy/${prefix}-*"
  ]

  managed_iam_role_arns = [
    for prefix in local.managed_iam_name_prefixes :
    "arn:aws:iam::${var.aws_account_id}:role/${prefix}-*"
  ]

  managed_iam_instance_profile_arns = [
    for prefix in local.managed_iam_name_prefixes :
    "arn:aws:iam::${var.aws_account_id}:instance-profile/${prefix}-*"
  ]

  tags = {
    Project     = "mrisk"
    Environment = var.app_env
    Owner       = var.owner
    CostCenter  = "LearningMVP"
    ManagedBy   = "Terraform"
  }

  tfc_subject = "organization:${var.tfc_organization}:project:${var.tfc_project}:workspace:${var.tfc_workspace}:run_phase:*"
}

data "tls_certificate" "tfc" {
  url = "https://app.terraform.io"
}

resource "aws_iam_openid_connect_provider" "tfc" {
  url = "https://app.terraform.io"

  client_id_list = [
    "aws.workload.identity",
  ]

  thumbprint_list = [
    data.tls_certificate.tfc.certificates[0].sha1_fingerprint,
  ]

  tags = local.tags
}

data "aws_iam_policy_document" "tfc_assume_role" {
  statement {
    effect = "Allow"

    actions = [
      "sts:AssumeRoleWithWebIdentity",
    ]

    principals {
      type = "Federated"
      identifiers = [
        aws_iam_openid_connect_provider.tfc.arn,
      ]
    }

    condition {
      test     = "StringEquals"
      variable = "app.terraform.io:aud"
      values   = ["aws.workload.identity"]
    }

    condition {
      test     = "StringLike"
      variable = "app.terraform.io:sub"
      values   = [local.tfc_subject]
    }
  }
}

resource "aws_iam_role" "tfc_deploy" {
  name               = "${local.name_prefix}-tfc-deploy"
  description        = "HCP Terraform deploy role for the dev stack."
  assume_role_policy = data.aws_iam_policy_document.tfc_assume_role.json
  tags               = local.tags
}

data "aws_iam_policy_document" "tfc_deploy" {
  statement {
    sid    = "ManageMriskServerlessResources"
    effect = "Allow"

    actions = [
      "apigateway:*",
      "budgets:*",
      "cloudfront:*",
      "cloudwatch:*",
      "cognito-idp:*",
      "dynamodb:*",
      "lambda:*",
      "logs:*",
      "s3:*",
      "sqs:*",
      "sts:GetCallerIdentity",
      "tag:GetResources",
      "tag:TagResources",
      "tag:UntagResources",
    ]

    resources = ["*"]
  }

  statement {
    sid    = "ListIamForTerraformReads"
    effect = "Allow"

    actions = [
      "iam:ListInstanceProfiles",
      "iam:ListInstanceProfilesForRole",
      "iam:ListOpenIDConnectProviders",
      "iam:ListPolicies",
      "iam:ListRoles",
    ]

    resources = ["*"]
  }

  statement {
    sid    = "ManageGithubOidcProvider"
    effect = "Allow"

    actions = [
      "iam:CreateOpenIDConnectProvider",
      "iam:DeleteOpenIDConnectProvider",
      "iam:GetOpenIDConnectProvider",
      "iam:ListOpenIDConnectProviderTags",
      "iam:TagOpenIDConnectProvider",
      "iam:UntagOpenIDConnectProvider",
      "iam:UpdateOpenIDConnectProviderThumbprint",
    ]

    resources = ["*"]
  }

  statement {
    sid    = "ManageMriskIam"
    effect = "Allow"

    actions = [
      "iam:AddRoleToInstanceProfile",
      "iam:AttachRolePolicy",
      "iam:CreatePolicy",
      "iam:CreatePolicyVersion",
      "iam:CreateRole",
      "iam:DeletePolicy",
      "iam:DeletePolicyVersion",
      "iam:DeleteRole",
      "iam:DeleteRolePolicy",
      "iam:DetachRolePolicy",
      "iam:GetInstanceProfile",
      "iam:GetPolicy",
      "iam:GetPolicyVersion",
      "iam:GetRole",
      "iam:GetRolePolicy",
      "iam:ListAttachedRolePolicies",
      "iam:ListPolicyVersions",
      "iam:ListRolePolicies",
      "iam:ListRoleTags",
      "iam:PassRole",
      "iam:PutRolePolicy",
      "iam:RemoveRoleFromInstanceProfile",
      "iam:TagOpenIDConnectProvider",
      "iam:TagPolicy",
      "iam:TagRole",
      "iam:UntagOpenIDConnectProvider",
      "iam:UntagPolicy",
      "iam:UntagRole",
      "iam:UpdateAssumeRolePolicy",
    ]

    resources = concat(
      local.managed_iam_policy_arns,
      local.managed_iam_role_arns,
      local.managed_iam_instance_profile_arns,
    )
  }
}

resource "aws_iam_role_policy" "tfc_deploy" {
  name   = "${local.name_prefix}-tfc-deploy"
  role   = aws_iam_role.tfc_deploy.id
  policy = data.aws_iam_policy_document.tfc_deploy.json
}
