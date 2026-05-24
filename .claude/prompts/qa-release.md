# Prompt: QA And Release Review

Use `qa-security-reviewer`.

Task: review the current implementation slice before completion.

Read:

- Changed files.
- `docs/security-governance.md`
- `docs/cost-plan.md`
- `docs/delivery-tasks.md`

Return findings first, ordered by severity. Include missing tests, security/privacy risks, cost risks, contract drift, `mrisk` Terraform/deploy drift, UI quality gaps, and verification performed.
