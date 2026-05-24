# API Contract

## Conventions

- Base path: `/api`
- Auth: Cognito JWT in `Authorization: Bearer <token>` for deployed environments.
- Response type: JSON.
- IDs: ULID or UUIDv7-style sortable identifiers.
- Timestamps: ISO 8601 UTC.

## Status Values

| Status | Meaning |
| --- | --- |
| `UPLOADED` | Submission record exists and upload URL was issued. |
| `QUEUED` | Processing job has been queued. |
| `OCR_RUNNING` | Text extraction is in progress. |
| `EXTRACTING` | Structured fields are being extracted. |
| `ENRICHING` | Public hazard data is being joined. |
| `GENERATING_SUMMARY` | Bedrock is generating the triage brief. |
| `READY` | Summary and extracted fields are available. |
| `NEEDS_REVIEW` | Processing completed but key data is missing or ambiguous. |
| `FAILED` | Processing failed after retry or validation failure. |

## POST `/submissions/upload-url`

Creates a submission record and returns a presigned S3 URL.

Request:

```json
{
  "fileName": "submission.pdf",
  "contentType": "application/pdf",
  "fileSizeBytes": 2450000
}
```

Response:

```json
{
  "submissionId": "01JZ4M8QZ6T9D4E2X7P2C9A1AB",
  "uploadUrl": "https://s3-presigned-url",
  "objectKey": "submissions/01JZ4M8QZ6T9D4E2X7P2C9A1AB/raw/submission.pdf",
  "expiresInSeconds": 900,
  "maxFileSizeBytes": 10000000
}
```

Validation:

- Allow `application/pdf`, `image/png`, `image/jpeg`, and `text/plain` for MVP.
- Reject files larger than the configured cap.
- Return `400` for unsupported content type.

## POST `/submissions/{submissionId}/start`

Queues processing after upload completes.

Request:

```json
{
  "objectKey": "submissions/01JZ4M8QZ6T9D4E2X7P2C9A1AB/raw/submission.pdf"
}
```

Response:

```json
{
  "submissionId": "01JZ4M8QZ6T9D4E2X7P2C9A1AB",
  "status": "QUEUED"
}
```

## GET `/submissions/{submissionId}`

Returns status and lightweight metadata for polling.

Response:

```json
{
  "submissionId": "01JZ4M8QZ6T9D4E2X7P2C9A1AB",
  "status": "ENRICHING",
  "createdAt": "2026-05-24T11:02:00Z",
  "updatedAt": "2026-05-24T11:02:38Z",
  "progress": {
    "currentStep": "Joining public hazard data",
    "percent": 65
  },
  "file": {
    "fileName": "submission.pdf",
    "contentType": "application/pdf"
  },
  "error": null
}
```

## GET `/submissions/{submissionId}/summary`

Returns extracted facts, enrichments, and generated summary. Only available for `READY` or `NEEDS_REVIEW`.

Response:

```json
{
  "submissionId": "01JZ4M8QZ6T9D4E2X7P2C9A1AB",
  "status": "READY",
  "extracted": {
    "insuredName": "Example Manufacturing LLC",
    "address": {
      "line1": "100 Example Ave",
      "city": "Los Angeles",
      "state": "CA",
      "postalCode": "90012",
      "countyFips": "06037"
    },
    "industry": "Light manufacturing",
    "requestedCoverage": "Commercial property",
    "limits": {
      "building": 5000000,
      "businessPersonalProperty": 1000000
    },
    "missingFields": ["constructionYear"]
  },
  "hazards": {
    "femaRiskRating": "Relatively High",
    "topHazards": ["Earthquake", "Wildfire", "Riverine Flooding"],
    "recentDisasterDeclarations": 4,
    "stormEventCounts10Yr": {
      "hail": 16,
      "strongWind": 83,
      "flashFlood": 21
    }
  },
  "aiBrief": {
    "executiveSummary": "This submission appears suitable for property market review but needs construction year confirmation.",
    "riskFlags": [
      "County hazard profile indicates elevated earthquake and wildfire exposure.",
      "Construction year is missing from the submission."
    ],
    "questionsForBroker": [
      "Confirm construction year and major renovations.",
      "Confirm wildfire mitigation measures and distance to vegetation."
    ],
    "confidence": "medium"
  },
  "sources": [
    {
      "name": "FEMA National Risk Index",
      "url": "https://hazards.fema.gov/nri/data-resources"
    },
    {
      "name": "NOAA Storm Events",
      "url": "https://www.ncdc.noaa.gov/stormevents/ftp.jsp"
    }
  ]
}
```

## GET `/submissions`

Lists recent submissions for the authenticated user.

Query parameters:

- `status`: optional status filter.
- `limit`: default `25`, max `100`.
- `nextToken`: pagination token.

