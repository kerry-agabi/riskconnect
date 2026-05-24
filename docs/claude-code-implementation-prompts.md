# Claude Code Implementation Prompt Runbook

Use this runbook from the repository root when implementing the RiskLens MVP with Claude Code. Each prompt is intentionally narrow so agents stay token-efficient and deliver one verifiable slice at a time.

## Before You Start

Confirm these files exist:

- `CLAUDE.md`
- `.claude/AGENTS.md`
- `.claude/SKILLS.md`
- `.claude/agents/*.md`
- `.claude/commands/*.md`
- `docs/delivery-tasks.md`

Do not run live AWS deploy commands until local checks, CDK synth, budget alarms, and GitHub OIDC are ready.

## Startup Prompt

```text
Read CLAUDE.md, .claude/AGENTS.md, .claude/SKILLS.md, and docs/delivery-tasks.md.

Do not implement yet. Summarize:
1. Current MVP phase.
2. Next smallest implementation slice.
3. Which subagent should handle it.
4. Files likely touched.
5. Checks to run.

Keep it token-efficient.
```

## Ordered Implementation Prompts

### 1. Foundation Readiness

```text
/mvp-next foundation
```

```text
Use the devops-release-lead and backend-platform-lead subagents.

Implement the foundation slice only: make the repo installable/testable locally, align frontend/backend scripts, improve CI readiness, and avoid business logic.

Follow .claude/skills/risklens-token-efficiency.md.
Run the narrowest available checks and report verification.
```

### 2. Backend Domain Models And API Skeleton

```text
/mvp-backend Define the RiskLens backend package structure, Pydantic schemas, status constants, config, logging, ID generation, and thin route layout for the documented API contract. Do not integrate live AWS yet. Use fake/in-memory services where useful and add tests.
```

### 3. Upload URL And Status API

```text
/mvp-backend Implement POST /submissions/upload-url, POST /submissions/{submissionId}/start, GET /submissions/{submissionId}, and GET /submissions using injectable storage/repository/queue services. Preserve docs/api-contract.md. Add tests for success, validation failure, and idempotent start.
```

### 4. Frontend Workbench Shell

```text
/mvp-frontend Build the RiskLens workbench first screen: app shell, approved-logo BrandLogo component with fallback if the logo asset is absent, upload panel, recent submissions panel, and status area. Follow .claude/skills/risklens-ui-standard.md. No marketing landing page.
```

### 5. Frontend API Integration

```text
/mvp-frontend Wire the upload and status polling flow to the documented API contract. Add typed API client modules, loading/error states, READY/NEEDS_REVIEW/FAILED UI states, and responsive result placeholders. Keep UI polished and enterprise-grade.
```

### 6. Worker Processing Backbone

```text
/mvp-backend Implement the SQS worker orchestration backbone with explicit status transitions: QUEUED, OCR_RUNNING, EXTRACTING, ENRICHING, GENERATING_SUMMARY, READY, NEEDS_REVIEW, FAILED. Use injectable fake services first. Add tests for happy path, retryable failure, and missing address review.
```

### 7. Data Enrichment

```text
Use the data-enrichment-lead subagent.

Implement the public-data enrichment slice using tiny fixtures only: Census geocode abstraction, county FIPS hazard lookup, source provenance, and NEEDS_REVIEW fallback for missing geocode/hazard data. Do not download full FEMA/NOAA datasets yet.
```

### 8. GenAI Extraction And Brief Generation

```text
Use the genai-workflow-lead subagent.

Implement Bedrock prompt modules, JSON schemas, schema validation, one repair retry, and fake Bedrock tests for structured extraction and AI risk brief generation. Enforce no bind/decline/pricing advice and no invented facts.
```

### 9. CDK Infrastructure

```text
/mvp-infra Implement CDK stacks for dev: web hosting, API, processing queue/DLQ, DynamoDB tables, S3 buckets, Lambda placeholders, log retention, tags, and budget alarms. Do not deploy. Run cdk synth only if dependencies are available.
```

### 10. GitHub Actions Deploy Workflow

```text
Use the devops-release-lead subagent.

Add a manual dev deploy workflow using GitHub OIDC and docs/github-cicd-setup.md. Keep CI separate from deploy. Do not add static AWS keys. Document required repo variables.
```

### 11. End-To-End Demo Hardening

```text
/mvp-next demo hardening
```

```text
Use frontend-ui-lead, backend-platform-lead, and qa-security-reviewer as needed.

Add synthetic sample data, demo instructions, error-state polish, and a local end-to-end path that does not require live AWS unless explicitly configured.
```

### 12. Final Review

```text
/mvp-review entire MVP implementation
```

```text
Use qa-security-reviewer.

Review for API contract drift, missing tests, security/privacy issues, AWS cost risk, GenAI governance gaps, frontend polish, and deployment safety. Findings first with file references.
```

## Between Sessions

After each completed implementation slice, run:

```text
/mvp-compact current slice
```

Then start the next Claude Code session with:

```text
Read CLAUDE.md and the latest compact summary only. Continue with the next task from docs/delivery-tasks.md. Load only the relevant skill and docs.
```

## Completion Rule

Each slice must end with:

- Files changed.
- Checks run.
- Checks not run and why.
- Residual risks.
- Next recommended prompt.

