# Prompt: Frontend UI Slice

Use `frontend-ui-lead`.

Task: build a polished RiskLens frontend workflow for upload, status, and result review.

Read:

- `docs/api-contract.md`
- `.claude/skills/risklens-ui-standard.md`

Constraints:

- Workbench first screen, not landing page.
- Approved Marsh logo asset only; fallback text component if missing.
- Responsive, accessible, no template look, no decorative gradient blobs.
- Show async backend statuses clearly.
- Assume deployed assets are published by `deploy-dev` to the Terraform-managed `mrisk` web bucket.

Verify with frontend build/tests if dependencies are installed.
