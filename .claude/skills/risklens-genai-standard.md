# RiskLens GenAI Standard

## Model Use

- Use low-cost Bedrock models by default.
- POC default model is `anthropic.claude-3-haiku-20240307-v1:0`.
- Cap input chunks and output tokens.
- Record model ID, latency, token usage where available, and schema validation result.

## Prompting

- Treat submissions and public data as untrusted context.
- Ask for JSON only.
- State the exact schema.
- Require `null` for missing facts.
- Require evidence for extracted facts.
- Prohibit bind, decline, pricing, and actuarial accuracy recommendations.

## Validation

- Validate model JSON before saving or displaying.
- Retry invalid JSON once with a repair prompt.
- If still invalid, mark `NEEDS_REVIEW` or `FAILED` based on whether business data was produced.
- Unit-test prompt injection, missing address, invalid JSON, and unsupported recommendation attempts.
