# Prompt: RiskLens Full Implementation Order

Use this when starting a fresh Claude Code implementation session for RiskLens.

For the deployed proof-of-concept path after infrastructure is available, use
`docs/poc-e2e-implementation-prompts.md`.

First:

```text
Read CLAUDE.md, .claude/AGENTS.md, .claude/SKILLS.md, and docs/delivery-tasks.md.

Do not implement yet. Summarize the current MVP phase, next smallest implementation slice, responsible subagent, likely files, and checks to run.
```

Then execute these prompts in order, one slice per session:

1. `/mvp-next foundation`
2. `Use the devops-release-lead and backend-platform-lead subagents. Implement the foundation slice only: make the repo installable/testable locally, align frontend/backend scripts, improve CI readiness, and avoid business logic.`
3. `/mvp-backend Define the RiskLens backend package structure, Pydantic schemas, status constants, config, logging, ID generation, and thin route layout for the documented API contract. Do not integrate live AWS yet. Use fake/in-memory services where useful and add tests.`
4. `/mvp-backend Implement POST /submissions/upload-url, POST /submissions/{submissionId}/start, GET /submissions/{submissionId}, and GET /submissions using injectable storage/repository/queue services. Preserve docs/api-contract.md. Add tests for success, validation failure, and idempotent start.`
5. `/mvp-frontend Build the RiskLens workbench first screen: app shell, approved-logo BrandLogo component with fallback if the logo asset is absent, upload panel, recent submissions panel, and status area. Follow .claude/skills/risklens-ui-standard.md. No marketing landing page.`
6. `/mvp-frontend Wire the upload and status polling flow to the documented API contract. Add typed API client modules, loading/error states, READY/NEEDS_REVIEW/FAILED UI states, and responsive result placeholders. Keep UI polished and enterprise-grade.`
7. `/mvp-backend Implement the SQS worker orchestration backbone with explicit status transitions: QUEUED, OCR_RUNNING, EXTRACTING, ENRICHING, GENERATING_SUMMARY, READY, NEEDS_REVIEW, FAILED. Use injectable fake services first. Add tests for happy path, retryable failure, and missing address review.`
8. `Use the data-enrichment-lead subagent. Implement the public-data enrichment slice using tiny fixtures only: Census geocode abstraction, county FIPS hazard lookup, source provenance, and NEEDS_REVIEW fallback for missing geocode/hazard data. Do not download full FEMA/NOAA datasets yet.`
9. `Use the genai-workflow-lead subagent. Implement Bedrock prompt modules, JSON schemas, schema validation, one repair retry, and fake Bedrock tests for structured extraction and AI risk brief generation. Enforce no bind/decline/pricing advice and no invented facts.`
10. `/mvp-infra Implement Terraform modules for dev: web hosting, API, processing queue/DLQ, DynamoDB tables, S3 buckets, Lambda placeholders, log retention, tags, budget alarms, and stack prefix mrisk. Do not apply. Run terraform fmt/init/validate only.`
11. `Use the devops-release-lead subagent. Maintain the manual dev deploy workflow using HCP Terraform plus GitHub OIDC for frontend assets. Keep CI separate from deploy. Do not add static AWS keys. Document required repo variables/secrets.`
12. `/mvp-next demo hardening`
13. `Use frontend-ui-lead, backend-platform-lead, and qa-security-reviewer as needed. Add synthetic sample data, demo instructions, error-state polish, and a local end-to-end path that does not require live AWS unless explicitly configured.`
14. `/mvp-review entire MVP implementation`

After each slice:

```text
/mvp-compact current slice
```

Each slice must report files changed, checks run, checks not run, residual risks, and the next recommended prompt.
