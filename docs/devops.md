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
- CDK synth.

Use a separate manual deploy workflow later:

- Authenticate to AWS using GitHub OIDC.
- Deploy CDK stacks.
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

