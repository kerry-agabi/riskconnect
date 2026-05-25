# Prompt: Backend API Slice

Use `backend-platform-lead`.

Task: implement one backend API/worker slice while preserving `docs/api-contract.md`.

Read:

- `docs/api-contract.md`
- `docs/poc-e2e-implementation-prompts.md`
- `.claude/skills/risklens-backend-standard.md`

Constraints:

- Thin routes, typed Pydantic schemas, injectable services.
- Structured logs without raw document text or secrets.
- Deterministic status transitions.
- SQS worker handlers report partial batch failures with `batchItemFailures`.
- Runtime AWS adapters stay behind service seams: S3, SQS, DynamoDB, Textract, Bedrock, Census, and hazard cache.
- Avoid hard-coded AWS resource names; deployment resources belong to the Terraform/HCP Terraform `mrisk` stack.
- Tests for success and failure paths.

Verify with backend lint/tests if dependencies are installed.
