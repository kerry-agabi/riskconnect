# RiskLens Submission Triage MVP

RiskLens is a low-budget GenAI MVP for commercial insurance submission triage. It helps a broker upload a property insurance submission, extract key facts, enrich the insured location with public hazard data, and produce an underwriter-ready risk brief.

The design is intentionally serverless-first for a small AWS credit budget. Frontend interactions stay fast while document OCR, enrichment, and GenAI summary generation run asynchronously in the backend.

## Repository Layout

- `docs/` - product, architecture, data, API, GenAI, security, DevOps, cost, and delivery documentation.
- `frontend/` - React application scaffold and delivery notes.
- `backend/` - Python backend scaffold for Lambda/API handlers and async workers.
- `infra/terraform/` - active Terraform/HCP Terraform infrastructure for stack `mrisk`.
- `infra/cdk/` - legacy AWS CDK scaffold retained for reference only.
- `infra/k8s/` - optional local Kubernetes manifests for portability demos.
- `.github/workflows/ci.yml` - CI for tests, Docker builds, Lambda packaging, and Terraform validation.
- `.github/workflows/deploy-dev.yml` - manual dev deploy workflow for stack `mrisk`.
- `docker-compose.yml` - local development topology.

Start with [docs/README.md](docs/README.md).
