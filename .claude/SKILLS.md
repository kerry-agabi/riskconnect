# RiskLens Project Skills

These project skill files are concise standards for Claude agents working on RiskLens. Load only the skill needed for the current task.

| Skill | Use For |
| --- | --- |
| `skills/risklens-token-efficiency.md` | Any multi-file task or long implementation session. |
| `skills/risklens-ui-standard.md` | Frontend UI, brand, accessibility, and responsive design. |
| `skills/risklens-backend-standard.md` | Python API, worker, logging, config, and service boundaries. |
| `skills/risklens-aws-standard.md` | Terraform/HCP Terraform, IAM, AWS naming, cost controls, deployment safety. |
| `skills/risklens-genai-standard.md` | Bedrock prompts, JSON schemas, governance, token controls. |

Rule: do not load all skills by default. Read the token-efficiency skill first, then the one domain skill relevant to the task.
