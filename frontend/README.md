# Frontend Scaffold

React frontend for RiskLens.

## Intended Stack

- React
- Vite
- TypeScript
- TanStack Query or SWR for polling
- Lightweight component styling with CSS modules or Tailwind

## Screens

- Submission upload
- Recent submissions list
- Processing status
- Risk brief review
- Error and `NEEDS_REVIEW` states

## Environment

```text
VITE_API_BASE_URL=http://localhost:8000
VITE_COGNITO_DOMAIN=
VITE_COGNITO_CLIENT_ID=
VITE_COGNITO_REDIRECT_URI=http://localhost:5173
VITE_COGNITO_LOGOUT_URI=http://localhost:5173
```

When Cognito variables are unset, the frontend leaves API requests
unauthenticated for local fake-service development. Deployed builds receive
Cognito variables from the `deploy-dev` workflow after Terraform outputs are
read.
