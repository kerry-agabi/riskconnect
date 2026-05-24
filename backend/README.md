# Backend Scaffold

Python backend for RiskLens.

## Intended Stack

- Python 3.12
- FastAPI for local API development
- AWS Lambda handlers for deployment
- boto3 for AWS integrations
- pydantic for request/response validation
- pytest for tests

## Backend Modules To Add

- `api/`: HTTP route handlers.
- `worker/`: SQS processing worker.
- `services/storage.py`: S3 helpers.
- `services/submissions.py`: DynamoDB status and event logic.
- `services/textract.py`: OCR integration.
- `services/bedrock.py`: model invocation and schema repair.
- `services/enrichment.py`: geocoding and hazard cache lookup.
- `schemas/`: pydantic models.
- `scripts/`: public data ingestion scripts.

