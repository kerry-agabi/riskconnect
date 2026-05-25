# RiskLens Backend Standard

## Structure

- `api/`: route handlers and HTTP translation.
- `core/`: config, logging, errors, IDs, constants.
- `schemas/`: Pydantic request/response/domain models.
- `services/`: business services and AWS wrappers.
- `repositories/`: persistence abstractions if DynamoDB logic grows.
- `worker/`: SQS orchestration and async processing.
- `tests/`: behavior-focused tests with fake services.

## Coding Rules

- Use explicit types and Pydantic validation at boundaries.
- Use dependency injection for AWS clients, repositories, clock, and ID generation.
- Keep route handlers thin.
- Keep AWS SDK calls out of route handlers.
- Keep runtime adapters for S3, SQS, DynamoDB, Textract, Bedrock, Census, and hazard cache behind service seams.
- Use domain constants for statuses; do not scatter string literals.
- Prefer idempotent operations for upload start and worker processing.
- SQS Lambda handlers must support partial batch failure responses.
- **Every Pydantic BaseModel must have a class-level docstring and a `description` on every Field.** Docstrings explain the model's purpose and usage context. Field descriptions explain what the value represents, valid ranges, and any constraints. This powers OpenAPI documentation and ensures schemas are self-documenting.

## Logging

- Use structured JSON logs.
- Include `correlation_id`, `submission_id`, `status`, and `component` when available.
- Do not log full document text, presigned URLs, raw Bedrock prompts with document content, credentials, or JWTs.

## Error Handling

- Translate expected validation errors into 4xx responses.
- Translate retryable service errors into worker retries.
- Store broker-readable failure reasons.
- Use `NEEDS_REVIEW` for missing/ambiguous business data.
