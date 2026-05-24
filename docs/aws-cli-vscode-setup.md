# AWS CLI Setup In VS Code Terminal

This guide sets up AWS CLI v2 for local RiskLens testing from the VS Code integrated terminal on Windows.

Official references:

- AWS CLI v2 install guide: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
- AWS CLI IAM Identity Center setup: https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html

## 1. Install AWS CLI v2

Download and run the Windows 64-bit MSI installer:

```powershell
msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi
```

Close and reopen VS Code after installation so the terminal picks up the updated `PATH`.

Verify:

```powershell
aws --version
```

Expected: an `aws-cli/2.x` version string.

## 2. Choose Region And Profile Names

Recommended MVP defaults:

```powershell
$env:AWS_REGION="us-east-1"
$env:AWS_PROFILE="risklens-dev"
```

Use a region where your account has Bedrock model access. For many accounts, `us-east-1` is the simplest starting point.

## 3. Configure IAM Identity Center

Prefer IAM Identity Center over long-lived IAM access keys.

Run:

```powershell
aws configure sso --profile risklens-dev
```

Enter:

- SSO start URL from AWS IAM Identity Center.
- SSO region.
- AWS account ID.
- Permission set, ideally a least-privilege developer or PowerUser-style permission set for the learning account.
- Default client region: `us-east-1`.
- Default output format: `json`.

Login:

```powershell
aws sso login --profile risklens-dev
```

Verify identity:

```powershell
aws sts get-caller-identity --profile risklens-dev
```

## 4. Configure Project Environment

Create local environment values from `.env.example` as needed. Do not commit real `.env` files.

For one terminal session:

```powershell
$env:AWS_PROFILE="risklens-dev"
$env:AWS_REGION="us-east-1"
$env:APP_ENV="dev"
```

For CDK commands:

```powershell
cd infra/cdk
cdk synth --profile risklens-dev
```

Do not run `cdk deploy` until the CDK stacks, budget alarms, and IAM permissions have been reviewed.

## 5. Check Bedrock Access

In the AWS console, request access to the selected low-cost Bedrock model before running live GenAI tests.

CLI identity check is not enough; Bedrock model access is managed separately in the Bedrock console.

## 6. Cost Safety Checklist

Before live testing:

- AWS Budgets alert configured.
- Worker concurrency capped.
- Upload size/page count limits enabled.
- No NAT Gateway, EKS, RDS, OpenSearch, provisioned Bedrock, or always-on EC2.
- Test with synthetic documents only.

## Troubleshooting

- If `aws` is not recognized, reopen VS Code or restart Windows.
- If SSO login fails, rerun `aws configure sso --profile risklens-dev`.
- If CDK cannot find credentials, confirm `$env:AWS_PROFILE` and run `aws sts get-caller-identity --profile risklens-dev`.
- If Bedrock calls fail with access errors, verify model access in the Bedrock console for the selected region.

