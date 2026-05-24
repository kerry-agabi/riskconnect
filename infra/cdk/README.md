# Legacy CDK Scaffold

This scaffold is retained for reference only. The active AWS infrastructure path is Terraform under `infra/terraform` for stack `mrisk`.

## Historical Stacks

- Web stack: S3 + CloudFront frontend hosting.
- API stack: API Gateway HTTP API, Cognito, API Lambda.
- Processing stack: submissions S3 bucket, SQS, DLQ, worker Lambda.
- Data stack: DynamoDB metadata and hazard cache tables.
- Observability stack: CloudWatch alarms and AWS Budgets.
