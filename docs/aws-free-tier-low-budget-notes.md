# Low-Budget AWS Notes

## Default Deployment Recommendation

Use serverless AWS for the actual cloud deployment:

- S3 and CloudFront for the frontend.
- API Gateway and Lambda for the API.
- SQS and Lambda for async workers.
- DynamoDB for metadata and hazard cache.
- Bedrock and Textract only when jobs require them.

This provides a realistic AWS microservices design without paying for idle compute.

## Kubernetes Practice Without EKS Cost

Use Kubernetes locally for learning:

- Docker Desktop Kubernetes or `kind`.
- Deploy the React container and backend API container locally.
- Keep AWS-managed serverless as the real MVP deployment.

This satisfies Kubernetes practice without consuming the AWS credit budget on cluster control plane and worker nodes.

## EC2/ECS Position

ECS Fargate is a good later option if the worker grows beyond Lambda limits, especially for heavy PDF parsing or batch data ingestion.

For the first MVP:

- Keep API on Lambda.
- Keep worker on Lambda.
- Run ingestion manually or through scheduled Lambda.
- Avoid EC2 unless a library cannot run in Lambda.

