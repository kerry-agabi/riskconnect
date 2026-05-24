# Optional Kubernetes Practice

These manifests are for local Kubernetes practice only. The default AWS deployment should remain serverless to protect the MVP budget.

## Local Use

```powershell
kubectl apply -f infra/k8s/
```

Expected local services:

- `risklens-frontend`
- `risklens-backend`

