# Prompt: GenAI Workflow Slice

Use `genai-workflow-lead`.

Task: implement one Bedrock prompt/schema/evaluation slice.

Read:

- `docs/genai-design.md`
- `.claude/skills/risklens-genai-standard.md`

Constraints:

- JSON-only outputs.
- Schema validation before display/persistence.
- One repair retry for invalid JSON.
- No invented facts, bind/decline/pricing, or actuarial claims.
- Token and cost caps.
- Live Bedrock permissions and worker runtime settings are managed by the Terraform/HCP Terraform `mrisk` stack.

Add tests for prompt injection and invalid JSON where relevant.
