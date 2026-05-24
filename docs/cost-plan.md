# Cost Plan

## Budget Target

Design target: stay under `$250` AWS credit for MVP development and demos.

The architecture avoids always-on services and uses serverless components wherever practical.

## Services Expected To Stay Low Cost

- S3 for small document and result storage.
- CloudFront for low demo traffic.
- API Gateway HTTP API for lightweight JSON requests.
- Lambda for intermittent API and worker execution.
- SQS for processing jobs.
- DynamoDB on-demand for small metadata and cache tables.

## Variable Cost Drivers

- Textract page count.
- Bedrock input/output tokens.
- Number and size of uploaded submissions.
- CloudWatch log volume.

## Hard Controls

- Max upload size: 10 MB for MVP.
- Max OCR pages: 25 pages per submission.
- Max concurrent workers: 2-5.
- Max Bedrock output tokens per task.
- Short CloudWatch log retention, recommended 14 days.
- S3 lifecycle policy for raw files, recommended 30-90 days.

## Services Intentionally Avoided

- EKS as the default deployment target.
- NAT Gateway.
- RDS.
- OpenSearch.
- Provisioned Bedrock throughput.
- Always-on EC2.

## Cost Monitoring

Create AWS Budgets alerts:

- `$100`: investigate spend.
- `$175`: stop bulk ingestion and reduce demo processing.
- `$225`: disable worker queue trigger until reviewed.

CloudWatch metrics to watch:

- Worker Lambda invocations and duration.
- SQS queue depth and DLQ messages.
- Bedrock invocation count.
- Textract page count, if available through billing/usage metrics.

## Pricing References

- AWS Lambda: https://aws.amazon.com/lambda/pricing/
- Amazon Bedrock: https://aws.amazon.com/bedrock/pricing/
- Amazon DynamoDB on-demand: https://aws.amazon.com/dynamodb/pricing/on-demand/
- Amazon S3: https://aws.amazon.com/s3/pricing/
- Amazon API Gateway: https://aws.amazon.com/api-gateway/pricing/
- Amazon Textract: https://aws.amazon.com/textract/pricing/

