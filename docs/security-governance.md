# Security and Governance

## Data Classification

Use synthetic submissions only for the MVP. Do not upload real client, policyholder, claim, or confidential Marsh data.

## Authentication

- Use Cognito hosted UI or simple Cognito user pools for deployed demo access.
- Require JWT auth for all API Gateway routes.
- Store user ID on each submission record.

## Authorization

- Users can read only their own submissions.
- Admin role can view operational metadata but not raw documents by default.
- API Lambda validates ownership before returning status or summary.

## Encryption

- S3 buckets encrypted with SSE-S3 or SSE-KMS.
- DynamoDB encryption enabled by default.
- TLS via CloudFront and API Gateway.

## PII Handling

The app may process names and addresses even with synthetic test data. Controls:

- Do not log full document text.
- Mask addresses in application logs where possible.
- Use short log retention for MVP.
- Add lifecycle expiration for uploaded raw submissions.

## GenAI Governance

- AI output is advisory and requires broker review.
- Prompt instructions prohibit binding, pricing, or decline recommendations.
- Store source metadata with every generated brief.
- Validate model JSON before presenting results.
- Display missing fields and confidence clearly.

## Audit Events

Record these events in DynamoDB:

- Submission created.
- File uploaded.
- Processing started.
- OCR completed.
- Bedrock extraction completed.
- Enrichment completed.
- Summary generated.
- Processing failed or moved to review.

## Threats and Mitigations

| Threat | Mitigation |
| --- | --- |
| Prompt injection in uploaded documents | Treat document text as untrusted context and constrain output schema. |
| Oversized files causing cost spikes | Enforce file size and page count limits. |
| Unauthorized document access | Cognito auth plus per-user ownership checks. |
| Public bucket exposure | Block public access and use CloudFront only for web assets. |
| Excessive Bedrock spend | Token caps, worker concurrency limits, and budget alarms. |

