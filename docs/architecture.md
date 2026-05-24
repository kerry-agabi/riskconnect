# Architecture

## High-Level Design

RiskLens uses a fast synchronous API for browser interactions and an asynchronous backend for expensive work such as OCR, data enrichment, and Bedrock calls.

```mermaid
flowchart LR
    User[Broker] --> CF[CloudFront]
    CF --> Web[S3 React App]
    User --> API[API Gateway HTTP API]
    API --> ApiLambda[Python API Lambda]
    ApiLambda --> DDB[(DynamoDB)]
    ApiLambda --> S3[(S3 Submissions)]
    S3 --> SQS[SQS Processing Queue]
    SQS --> Worker[Python Worker Lambda]
    Worker --> Textract[Textract]
    Worker --> Bedrock[Amazon Bedrock]
    Worker --> PublicData[(S3/Dynamo Hazard Cache)]
    Worker --> DDB
    Worker --> Results[(S3 Results)]
```

## Runtime Flow

```mermaid
sequenceDiagram
    participant UI as React UI
    participant API as API Gateway
    participant L1 as API Lambda
    participant S3 as S3
    participant Q as SQS
    participant W as Worker Lambda
    participant TX as Textract
    participant BR as Bedrock
    participant DB as DynamoDB

    UI->>API: POST /submissions/upload-url
    API->>L1: Create upload intent
    L1->>DB: Put submission status=UPLOADED
    L1->>S3: Create presigned URL
    L1-->>UI: submissionId + uploadUrl
    UI->>S3: PUT PDF
    UI->>API: POST /submissions/{id}/start
    L1->>Q: Send processing message
    L1->>DB: status=QUEUED
    UI->>API: GET /submissions/{id}
    Q->>W: Deliver job
    W->>DB: status=OCR_RUNNING
    W->>TX: Extract text
    W->>DB: status=EXTRACTING
    W->>BR: Extract structured fields
    W->>DB: status=ENRICHING
    W->>DB: Read hazard cache by county/FIPS
    W->>DB: status=GENERATING_SUMMARY
    W->>BR: Generate underwriting brief
    W->>S3: Store text and report artifacts
    W->>DB: status=READY
    UI->>API: GET /submissions/{id}/summary
```

## Core Components

- React frontend: upload, progress, triage dashboard, and result review.
- API Lambda: low-latency request handling, auth checks, presigned URLs, status reads.
- Worker Lambda: asynchronous OCR, extraction, enrichment, and GenAI generation.
- DynamoDB: source of truth for submission metadata and status transitions.
- S3: raw uploads, extracted text, generated reports, cached public datasets.
- SQS: decouples frontend and backend processing; supports retry and DLQ handling.
- Bedrock: structured extraction and underwriting brief generation.
- Textract: OCR for PDFs/images. Text-native PDFs can use lightweight local parsing first to reduce cost.

## Latency Strategy

- Browser upload uses S3 presigned URLs, avoiding API Gateway payload bottlenecks.
- API calls return small JSON payloads and avoid OCR/LLM work.
- Long work is pushed to SQS and processed asynchronously.
- Frontend polls status every 2-5 seconds with exponential backoff after 60 seconds.
- Generated reports are loaded only when the status is `READY`.

## Scalability Strategy

- SQS absorbs traffic spikes.
- Worker Lambda concurrency is capped to control cost.
- DynamoDB uses on-demand capacity for unpredictable MVP traffic.
- Public datasets are cached in S3/DynamoDB rather than fetched per submission.
- The design can later split extraction, enrichment, and summary generation into separate queues if throughput requires it.

## Failure Handling

- Failed worker jobs retry through SQS redrive policy.
- Poison messages go to a DLQ after the configured retry count.
- Submission status changes to `FAILED` only after retries are exhausted or a non-retryable validation failure occurs.
- `NEEDS_REVIEW` is used when the document processes but required fields such as address or occupancy are missing.

