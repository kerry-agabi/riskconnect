# Prompt: GenAI Workflow Slice

Use `genai-workflow-lead`.

Task: implement one Bedrock prompt/schema/evaluation slice.

Read:

- `docs/genai-design.md`
- `docs/poc-e2e-implementation-prompts.md`
- `.claude/skills/risklens-genai-standard.md`

Constraints:

- JSON-only outputs.
- Schema validation before display/persistence.
- One repair retry for invalid JSON.
- No invented facts, bind/decline/pricing, or actuarial claims.
- Token and cost caps.
- Default POC model is the EU Claude Sonnet 4.6 inference profile `eu.anthropic.claude-sonnet-4-6` unless docs and Terraform are updated together. Newer Sonnet models require the Bedrock inference profile ID/ARN, not the direct base model ID.
- Live Bedrock permissions and worker runtime settings are managed by the Terraform/HCP Terraform `mrisk` stack.

Add tests for prompt injection and invalid JSON where relevant.
