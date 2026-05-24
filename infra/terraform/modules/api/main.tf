data "aws_iam_policy_document" "api_assume_role" {
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

resource "aws_iam_role" "api" {
  name               = "${var.name_prefix}-api-lambda"
  assume_role_policy = data.aws_iam_policy_document.api_assume_role.json
  tags               = var.tags
}

data "aws_iam_policy_document" "api" {
  statement {
    effect = "Allow"

    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]

    resources = [
      "${aws_cloudwatch_log_group.api.arn}:*",
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "s3:AbortMultipartUpload",
      "s3:PutObject",
    ]

    resources = [
      "${var.submissions_bucket_arn}/submissions/*",
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "sqs:SendMessage",
    ]

    resources = [
      var.processing_queue_arn,
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "dynamodb:BatchGetItem",
      "dynamodb:BatchWriteItem",
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:Query",
      "dynamodb:UpdateItem",
    ]

    resources = [
      var.submissions_table_arn,
      "${var.submissions_table_arn}/index/*",
      var.hazards_table_arn,
    ]
  }
}

resource "aws_iam_role_policy" "api" {
  name   = "${var.name_prefix}-api"
  role   = aws_iam_role.api.id
  policy = data.aws_iam_policy_document.api.json
}

resource "aws_cloudwatch_log_group" "api" {
  name              = "/aws/lambda/${var.name_prefix}-api"
  retention_in_days = var.log_retention_days
  tags              = var.tags
}

resource "aws_lambda_function" "api" {
  function_name    = "${var.name_prefix}-api"
  role             = aws_iam_role.api.arn
  runtime          = "python3.12"
  handler          = "api_handler.handler"
  filename         = var.api_lambda_package_path
  source_code_hash = try(filebase64sha256(var.api_lambda_package_path), null)
  timeout          = 10
  memory_size      = 512

  environment {
    variables = {
      AWS_REGION            = var.aws_region
      DYNAMODB_TABLE        = var.submissions_table_name
      HAZARDS_TABLE         = var.hazards_table_name
      LOG_LEVEL             = "INFO"
      S3_BUCKET             = var.submissions_bucket_name
      SQS_QUEUE_URL         = var.processing_queue_url
      SUBMISSIONS_BUCKET    = var.submissions_bucket_name
      SUBMISSIONS_TABLE     = var.submissions_table_name
      UPLOAD_EXPIRY_SECONDS = "900"
      MAX_FILE_SIZE_BYTES   = "10000000"
    }
  }

  depends_on = [
    aws_cloudwatch_log_group.api,
    aws_iam_role_policy.api,
  ]

  tags = var.tags
}

resource "aws_apigatewayv2_api" "api" {
  name          = "${var.name_prefix}-http-api"
  protocol_type = "HTTP"

  cors_configuration {
    allow_headers = ["authorization", "content-type"]
    allow_methods = ["GET", "POST", "OPTIONS"]
    allow_origins = ["*"]
    max_age       = 300
  }

  tags = var.tags
}

resource "aws_apigatewayv2_integration" "api" {
  api_id                 = aws_apigatewayv2_api.api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.api.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "default" {
  api_id    = aws_apigatewayv2_api.api.id
  route_key = "$default"
  target    = "integrations/${aws_apigatewayv2_integration.api.id}"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.api.id
  name        = "$default"
  auto_deploy = true
  tags        = var.tags
}

resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowExecutionFromApiGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.api.execution_arn}/*/*"
}

