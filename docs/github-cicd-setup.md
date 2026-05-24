# GitHub CI/CD Setup

This guide sets up version control and CI/CD for the RiskLens MVP.

Official references:

- GitHub Actions OIDC with AWS: https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws
- AWS credentials action: https://github.com/aws-actions/configure-aws-credentials

## 1. Initialize Version Control

From the repo root:

```powershell
git init
git add .
git commit -m "chore: initialize risklens mvp"
```

Recommended branch model:

- `main`: deployable trunk.
- Feature branches: `feature/<short-name>`.
- Pull requests required for merges.

Use concise conventional commits:

- `feat: add upload status api`
- `fix: handle missing geocode result`
- `docs: add aws cli setup`
- `chore: update ci`

## 2. Protect Secrets

Never commit:

- `.env` or `.env.*`
- AWS access keys
- SSO cache files
- Raw submissions
- Raw public data dumps
- CDK output
- Frontend build output

The `.gitignore` and `.claude/settings.json` are configured to reduce accidental exposure.

## 3. Configure GitHub Repository

Create a GitHub repository and push:

```powershell
git remote add origin https://github.com/<owner>/<repo>.git
git branch -M main
git push -u origin main
```

Enable branch protection for `main`:

- Require pull request before merging.
- Require status checks.
- Require branches to be up to date before merging.
- Block force pushes.
- Block deletions.

## 4. Configure AWS OIDC For GitHub Actions

Prefer OIDC over static AWS keys.

Create an IAM OIDC provider:

- Provider URL: `https://token.actions.githubusercontent.com`
- Audience: `sts.amazonaws.com`

Create a deploy role such as:

```text
risklens-github-actions-deploy-role
```

Trust policy shape:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::<AWS_ACCOUNT_ID>:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:<OWNER>/<REPO>:ref:refs/heads/main"
        }
      }
    }
  ]
}
```

Use least privilege for the role. During early MVP development, a scoped CDK deploy policy may be broader than final production policy, but it must be limited to the RiskLens dev account and reviewed before use.

## 5. Repository Variables And Secrets

Use repository variables:

- `AWS_REGION`: `us-east-1`
- `APP_ENV`: `dev`
- `CDK_DEFAULT_ACCOUNT`: AWS account ID
- `CDK_DEPLOY_ROLE_ARN`: OIDC deploy role ARN

Avoid repository secrets for AWS access keys. If a temporary key fallback is unavoidable, rotate it after use and remove it once OIDC works.

## 6. CI Workflow

The existing `.github/workflows/ci.yml` should validate:

- Frontend install/build.
- Backend install, ruff, pytest.
- Docker builds.
- CDK synth.

Recommended improvements as implementation matures:

- Add dependency caching after lockfiles exist.
- Add frontend unit tests once UI tests exist.
- Add `mypy` once backend types stabilize.
- Upload build/test artifacts only when useful.

## 7. Manual Deploy Workflow

Add a separate manual workflow later, for example `.github/workflows/deploy-dev.yml`.

Required workflow permissions:

```yaml
permissions:
  id-token: write
  contents: read
```

Credential step:

```yaml
- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: ${{ vars.CDK_DEPLOY_ROLE_ARN }}
    aws-region: ${{ vars.AWS_REGION }}
```

Deployment steps:

```yaml
- run: npm install -g aws-cdk
- run: python -m pip install -r requirements.txt
  working-directory: infra/cdk
- run: cdk deploy --all --require-approval never
  working-directory: infra/cdk
```

Keep deploy manual until costs and stack permissions are stable.

## 8. Release Checklist

Before running a deploy:

- CI passes on `main`.
- `cdk synth` reviewed.
- AWS budget alert exists.
- Bedrock model access confirmed.
- No real client data in test fixtures.
- No expensive services added.
- Rollback plan is documented in the pull request.

