# AWS Infrastructure

## CDK Stack Overview

Use AWS CDK in Python under `infra/cdk/`.

Stacks:

- `RiskLensWebStack`: S3 static website bucket, CloudFront distribution, deployment role.
- `RiskLensApiStack`: API Gateway HTTP API, API Lambda, Cognito authorizer.
- `RiskLensProcessingStack`: S3 submissions bucket, SQS queue, DLQ, worker Lambda, Textract/Bedrock permissions.
- `RiskLensDataStack`: DynamoDB tables and S3 public data cache bucket.
- `RiskLensObservabilityStack`: CloudWatch alarms, dashboard, AWS Budgets notifications.

## AWS Services

| Service | Purpose | Budget Notes |
| --- | --- | --- |
| S3 | Static app, raw submissions, results, public data cache | Low cost for MVP volumes. |
| CloudFront | Fast frontend delivery | Free tier friendly for low traffic. |
| Cognito | Demo authentication | Avoid custom auth implementation. |
| API Gateway HTTP API | Low-latency API | Cheaper than REST API for MVP. |
| Lambda | API handlers and async processing | Pay per request/duration. |
| SQS | Decoupled processing queue | Very low cost. |
| DynamoDB on-demand | Status, metadata, hazard cache | No capacity planning. |
| Textract | OCR for PDFs/images | Use page caps to control cost. |
| Bedrock | GenAI extraction and summaries | Use Haiku/Nova-class model and token caps. |
| CloudWatch | Logs, metrics, alarms | Set log retention to 14 days. |
| AWS Budgets | Cost guardrail | Alert before credit exhaustion. |

## IAM Principles

- API Lambda can create presigned URLs only for the submissions prefix.
- Worker Lambda can read raw submission objects and write result artifacts.
- Worker Lambda can call Textract and Bedrock only for required actions.
- No wildcard admin policies.
- Separate deploy role for GitHub Actions using OIDC.

## DynamoDB Tables

### `RiskLensSubmissions`

Partition key: `pk`

Sort key: `sk`

Records:

- `pk=SUBMISSION#{id}`, `sk=METADATA`
- `pk=SUBMISSION#{id}`, `sk=EVENT#{timestamp}`

Global secondary index:

- `gsi1pk=USER#{userId}`
- `gsi1sk={createdAt}`

### `RiskLensHazards`

Partition key: `pk`

Sort key: `sk`

Records:

- `pk=COUNTY#{fips}`, `sk=HAZARD_SUMMARY#latest`
- `pk=COUNTY#{fips}`, `sk=SOURCE_VERSION#{sourceName}`

## S3 Buckets

- `risklens-web-{account}-{region}`: frontend build artifacts.
- `risklens-submissions-{account}-{region}`: raw uploads and generated outputs.
- `risklens-data-cache-{account}-{region}`: public data snapshots.

Use encryption at rest, block public access, and lifecycle expiration for temporary artifacts.

## SQS

- Main queue: `risklens-processing`
- DLQ: `risklens-processing-dlq`
- Visibility timeout: at least 6x worker Lambda timeout.
- Max receive count: `3`.

## Lambda Settings

API Lambda:

- Runtime: Python 3.12
- Timeout: 10 seconds
- Memory: 512 MB

Worker Lambda:

- Runtime: Python 3.12
- Timeout: 5-10 minutes
- Memory: 1024-2048 MB depending on PDF parsing library needs
- Reserved concurrency: low single digits for cost control

## Budget Alarms

Create AWS Budgets alerts at:

- `$100`: early warning
- `$175`: reduce test volume
- `$225`: stop nonessential processing

