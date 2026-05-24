# DevOps

## Branching

- `main`: deployable trunk.
- Feature branches: short-lived branches for implementation tasks.
- Pull requests required before merging to `main`.

## GitHub Actions

Use `.github/workflows/ci.yml` for:

- Frontend install, lint, test, and build.
- Backend install, lint, type check, and unit tests.
- Docker image build checks.
- Lambda artifact packaging.
- Terraform format/init/validate checks for `infra/terraform/dev` and `infra/terraform/bootstrap`.

Use `.github/workflows/deploy-dev.yml` for the manual dev deploy:

- Run Terraform CLI against HCP Terraform. During the old-role fallback, `TERRAFORM_PROJECT_NAME=riskconnect` keeps AWS resources under the `riskconnect-dev-*` prefix.
- Let HCP Terraform assume the AWS run role through workload identity.
- Upload frontend build to S3.
- Invalidate CloudFront.

## Local Development

Recommended commands once implementation dependencies are added:

```powershell
docker compose up --build
```

Frontend:

```powershell
cd frontend
npm install
npm run dev
```

Backend:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\python -m pip install -e ".[dev]"
.venv\Scripts\python -m pytest
```

## Docker

Dockerfiles are included for:

- React/Vite development and build validation.
- Python backend API/worker local development.

Production AWS runtime should use Lambda packages or container images only if dependency size requires it.

## Active Infrastructure

- Stack name: `mrisk`.
- Temporary AWS resource prefix: `riskconnect-dev` while using the old HCP Terraform run role.
- Terraform root: `infra/terraform/dev`.
- HCP Terraform organization: `ka-risklens-mm`.
- HCP Terraform workspace: `riskconnect-dev`.
- AWS region: `eu-west-1`.

The CDK scaffold under `infra/cdk/` is legacy reference only.

## Kubernetes

Kubernetes is included as an optional portability exercise under `infra/k8s/`.

Default AWS deployment should not use EKS because the account has a low credit budget. For practice, use:

- `kind` or Docker Desktop Kubernetes locally.
- Simple frontend and backend deployments.
- ConfigMaps for environment variables.
- No production secrets in manifests.

## Environment Promotion

MVP environments:

- `local`: Docker Compose and local mocks.
- `dev`: AWS serverless deployment for demos.

Do not create `staging` or `prod` until the MVP proves value.
