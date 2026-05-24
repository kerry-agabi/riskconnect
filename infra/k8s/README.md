# Optional Kubernetes Practice

These manifests are for local Kubernetes practice only. The default AWS deployment should remain serverless to protect the MVP budget.

The active AWS stack name is `mrisk`; these Kubernetes resource names remain local-only demo names and are not part of the deployed `mrisk` stack.

## Local Use

```powershell
kubectl apply -f infra/k8s/
```

Expected local services:

- `risklens-frontend`
- `risklens-backend`
