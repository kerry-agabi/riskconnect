resource "aws_s3_bucket" "submissions" {
  bucket        = "${var.name_prefix}-submissions-${var.aws_account_id}-${var.aws_region}"
  force_destroy = var.force_destroy_buckets
  tags          = var.tags
}

resource "aws_s3_bucket_public_access_block" "submissions" {
  bucket                  = aws_s3_bucket.submissions.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "submissions" {
  bucket = aws_s3_bucket.submissions.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_versioning" "submissions" {
  bucket = aws_s3_bucket.submissions.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "submissions" {
  bucket = aws_s3_bucket.submissions.id

  rule {
    id     = "expire-temporary-submission-artifacts"
    status = "Enabled"

    filter {
      prefix = "submissions/"
    }

    noncurrent_version_expiration {
      noncurrent_days = 14
    }

    expiration {
      days = 90
    }
  }
}

resource "aws_sqs_queue" "dlq" {
  name                      = "${var.name_prefix}-processing-dlq"
  message_retention_seconds = 1209600
  sqs_managed_sse_enabled   = true
  tags                      = var.tags
}

resource "aws_sqs_queue" "processing" {
  name                       = "${var.name_prefix}-processing"
  visibility_timeout_seconds = 360
  message_retention_seconds  = 345600
  sqs_managed_sse_enabled    = true

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dlq.arn
    maxReceiveCount     = 3
  })

  tags = var.tags
}

data "aws_iam_policy_document" "worker_assume_role" {
  statement {
    effect = "Allow"

    actions = [
      "sts:AssumeRole",
    ]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "worker" {
  name               = "${var.name_prefix}-worker-lambda"
  assume_role_policy = data.aws_iam_policy_document.worker_assume_role.json
  tags               = var.tags
}

data "aws_iam_policy_document" "worker" {
  statement {
    effect = "Allow"

    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]

    resources = [
      "${aws_cloudwatch_log_group.worker.arn}:*",
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "s3:GetObject",
      "s3:PutObject",
    ]

    resources = [
      "${aws_s3_bucket.submissions.arn}/submissions/*",
      "${aws_s3_bucket.submissions.arn}/results/*",
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "sqs:ChangeMessageVisibility",
      "sqs:DeleteMessage",
      "sqs:GetQueueAttributes",
      "sqs:ReceiveMessage",
    ]

    resources = [
      aws_sqs_queue.processing.arn,
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "bedrock:InvokeModel",
      "textract:AnalyzeDocument",
      "textract:DetectDocumentText",
      "textract:GetDocumentAnalysis",
      "textract:GetDocumentTextDetection",
      "textract:StartDocumentAnalysis",
      "textract:StartDocumentTextDetection",
    ]

    resources = ["*"]
  }

  statement {
    effect = "Allow"

    actions = [
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:UpdateItem",
    ]

    resources = [
      var.submissions_table_arn,
      var.hazards_table_arn,
    ]
  }
}

resource "aws_iam_role_policy" "worker" {
  name   = "${var.name_prefix}-worker"
  role   = aws_iam_role.worker.id
  policy = data.aws_iam_policy_document.worker.json
}

resource "aws_cloudwatch_log_group" "worker" {
  name              = "/aws/lambda/${var.name_prefix}-worker"
  retention_in_days = var.log_retention_days
  tags              = var.tags
}

resource "aws_lambda_function" "worker" {
  function_name                  = "${var.name_prefix}-worker"
  role                           = aws_iam_role.worker.arn
  runtime                        = "python3.12"
  handler                        = "worker_handler.handler"
  filename                       = var.worker_lambda_package_path
  source_code_hash               = try(filebase64sha256(var.worker_lambda_package_path), null)
  timeout                        = 300
  memory_size                    = 1024
  reserved_concurrent_executions = var.worker_reserved_concurrency

  environment {
    variables = {
      AWS_ACCOUNT_ID     = var.aws_account_id
      BEDROCK_MODEL_ID   = "anthropic.claude-sonnet-4-6"
      HAZARDS_TABLE      = var.hazards_table_name
      S3_BUCKET          = aws_s3_bucket.submissions.bucket
      SUBMISSIONS_BUCKET = aws_s3_bucket.submissions.bucket
      SUBMISSIONS_TABLE  = var.submissions_table_name
      QUEUE_URL          = aws_sqs_queue.processing.url
      LOG_LEVEL          = "INFO"
    }
  }

  depends_on = [
    aws_cloudwatch_log_group.worker,
    aws_iam_role_policy.worker,
  ]

  tags = var.tags
}

resource "aws_lambda_event_source_mapping" "processing" {
  event_source_arn        = aws_sqs_queue.processing.arn
  function_name           = aws_lambda_function.worker.arn
  batch_size              = 5
  function_response_types = ["ReportBatchItemFailures"]
  enabled                 = true
}
