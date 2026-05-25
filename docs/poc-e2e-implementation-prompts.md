# RiskLens POC E2E Implementation Prompts

Use this runbook from the repository root to implement and verify the deployed
RiskLens proof of concept. Each prompt is narrow, assigns the relevant project
agent, and ends with concrete checks.

## Source Anchors

- Public PDF: City of Los Angeles certificate of occupancy PDF for `14350 VICTORY BLVD`: https://cityclerk.lacity.org/onlinedocs/2014/14-1582_misc_11-19-14.pdf
- Geocoder: US Census Geocoder: https://www.census.gov/programs-surveys/geography/technical-documentation/complete-technical-documentation/census-geocoder.html
- Hazard data: FEMA National Risk Index: https://hazards.fema.gov/nri/data-resources
- Disaster data: OpenFEMA Disaster Declarations Summaries: https://www.fema.gov/about/openfema/disaster-declarations-summaries
- Weather data: NOAA Storm Events Database: https://www.ncei.noaa.gov/stormevents/ftp.jsp

## Current Deploy Defaults

- Product label: `STACK_NAME=mrisk`
- Temporary Terraform resource prefix: `TERRAFORM_PROJECT_NAME=riskconnect`
- HCP Terraform workspace: `riskconnect-dev`
- HCP Terraform AWS run role: `arn:aws:iam::178002661103:role/riskconnect-dev-tfc-deploy`
- AWS region: `eu-west-1`

Do not run live deploys or Bedrock/Textract calls until local tests, Terraform
validation, Cognito configuration, and budget alarms have been checked.

## Prompt 1: Readiness Check

```text
Use devops-release-lead and qa-security-reviewer.

Inspect current uncommitted work without reverting it. Confirm the worker
orchestrator, fixture enrichment, frontend summary panel, and deploy fallback
are present. Report:
1. files already changed,
2. slices still missing for a live POC,
3. exact checks to run before deploy.
Do not implement.
```

## Prompt 2: Cognito Auth

```text
Use aws-infra-lead and frontend-ui-lead.

Add Cognito Hosted UI auth for the deployed dev POC. Terraform must create the
user pool, app client, domain, and HTTP API JWT authorizer. Frontend must use a
browser-native Authorization Code + PKCE flow, inject JWTs via setAuthTokenProvider,
refresh tokens before expiry when possible, and redirect on backend 401.

Keep dependencies minimal; do not add a large auth SDK unless strictly needed.
Run frontend tests, build, and Terraform validate.
```

## Prompt 3: Recent Submissions

```text
Use frontend-ui-lead.

Add nextToken pagination and periodic refresh to the Recent Submissions list.
Show Load more only when nextToken is present. Refresh every 15 seconds while
any row is QUEUED, OCR_RUNNING, EXTRACTING, ENRICHING, or GENERATING_SUMMARY.
Avoid duplicate rows across pages.

Run focused frontend tests and build.
```

## Prompt 4: Runtime API Persistence

```text
Use backend-platform-lead.

Replace Lambda runtime fake storage/queue/status paths with AWS-backed services:
S3 presigned upload, SQS processing message, DynamoDB submission metadata,
DynamoDB status transitions, and persisted summary retrieval. Preserve existing
fake services and tests for local API behavior.

Do not log presigned URLs, JWTs, or raw document text. Run backend tests.
```

## Prompt 5: SQS Worker Handler

```text
Use backend-platform-lead.

Replace the worker placeholder Lambda with a real SQS handler. Parse event
batches into ProcessingMessage models, call SubmissionProcessor, and return
batchItemFailures for retryable or malformed messages. NonRetryableError must
mark FAILED through the processor and not fail the batch item.

Update Lambda packaging and Terraform handler/event source mapping for
ReportBatchItemFailures. Run worker tests and Terraform validate.
```

## Prompt 6: Public Data Adapters

```text
Use data-enrichment-lead.

Implement CensusGeocodeService and DynamoHazardRepository behind the existing
GeocodeService and HazardRepository protocols. Add a small ingestion CLI that
downloads the selected public PDF to data/raw, writes a compact Los Angeles
County hazard record to data/processed, and can load that record into the
Terraform-managed hazards DynamoDB table.

Keep raw and generated data git-ignored. Preserve source URLs and snapshot dates.
Run enrichment tests.
```

## Prompt 7: Textract And Bedrock

```text
Use genai-workflow-lead and backend-platform-lead.

Implement live text extraction and Bedrock adapters behind the existing worker
protocols. Use Textract async document text detection for PDF input. Use one
bounded Bedrock extraction prompt and one bounded triage-brief prompt.

Defaults:
- model: anthropic.claude-3-haiku-20240307-v1:0
- max input text: 8000 characters
- extraction output cap: 800 tokens
- brief output cap: 500 tokens
- one JSON repair retry

Never produce bind, decline, pricing, or actuarial recommendations. Run schema
and worker tests with fakes/stubs.
```

## Prompt 8: Live POC Smoke

```text
Use devops-release-lead and qa-security-reviewer.

After explicit approval for live AWS execution, deploy dev, create a Cognito
test user, load the Los Angeles hazard record, upload the public PDF through the
frontend, and verify one submission reaches READY or a clear NEEDS_REVIEW state.

Record frontend URL, submission ID, final status, source links shown, CloudWatch
log groups checked, and approximate Textract/Bedrock invocation count.
```

## Prompt 9: Final Review

```text
Use qa-security-reviewer.

Review the deployed POC for API contract drift, auth gaps, IAM overreach, raw
document logging, model-cost controls, failure handling, UI usability, and
rollback steps. Findings first, ordered by severity, with file references.
```

