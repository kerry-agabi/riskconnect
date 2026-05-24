# RiskLens Claude Project Memory

## Project Context

RiskLens is a low-budget GenAI MVP for commercial insurance submission triage. It uses a React frontend, Python backend, and AWS serverless services to upload property submissions, extract facts, enrich locations with public hazard data, and generate a broker-reviewable underwriting triage brief.

Read these first, only as needed:

- Product overview: `docs/README.md`
- Architecture: `docs/architecture.md`
- API contract: `docs/api-contract.md`
- GenAI rules: `docs/genai-design.md`
- AWS infra: `docs/aws-infrastructure.md`
- Delivery backlog: `docs/delivery-tasks.md`

## Non-Negotiables

- Do not process, create, or request real client/confidential Marsh data.
- Keep frontend interactions fast; long OCR/enrichment/Bedrock work must be async.
- Keep AWS budget under the low-credit target: no default EKS, NAT Gateway, RDS, OpenSearch, provisioned Bedrock, or always-on EC2.
- Use approved Marsh logo assets only. Do not scrape, recreate, redraw, or approximate the official logo.
- Do not commit `.env`, AWS credentials, raw downloaded public datasets, generated build output, or raw submission documents.
- Preserve the documented API contract unless explicitly updating both implementation and docs.

## Token Efficiency

- Inspect targeted files first with `rg`/`ls`/short reads.
- Load only the docs needed for the current task.
- Prefer small, isolated changes with clear acceptance checks.
- Summarize long findings instead of pasting whole files.
- Use `.claude/skills/risklens-token-efficiency.md` before large implementation work.

## Engineering Standards

- Frontend must look like a polished enterprise insurance workflow, not a generic AI template.
- Backend must use typed schemas, dependency injection seams, structured logging, reusable service boundaries, and testable AWS wrappers.
- Infrastructure must use consistent names, tags, least privilege, budget alarms, and environment-aware config.
- GenAI outputs must be schema-validated, evidence-grounded, and explicitly framed as broker-reviewable drafts.

