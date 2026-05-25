from __future__ import annotations

import os

from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Application configuration loaded from environment variables with defaults.

    Controls runtime behavior of the API Lambda including storage locations,
    queue endpoints, file size limits, and logging verbosity. In tests, override
    via FastAPI dependency injection.
    """

    app_name: str = Field(
        "RiskLens API",
        description="Display name of the application, used in health check responses.",
    )
    s3_bucket: str = Field(
        "risklens-submissions-dev",
        description="S3 bucket name for storing uploaded submission documents.",
    )
    sqs_queue_url: str = Field(
        "",
        description="SQS queue URL for dispatching async processing jobs.",
    )
    submissions_table: str = Field(
        "",
        description="DynamoDB table name for submission metadata and summaries.",
    )
    hazards_table: str = Field(
        "",
        description="DynamoDB table name for county hazard cache records.",
    )
    bedrock_model_id: str = Field(
        "eu.anthropic.claude-sonnet-4-6",
        description="Amazon Bedrock model or inference profile ID for extraction and triage brief generation.",
    )
    bedrock_max_input_chars: int = Field(
        8000,
        description="Maximum extracted text characters sent to Bedrock per task.",
    )
    aws_region: str = Field(
        "us-east-1",
        description="AWS region for all service clients.",
    )
    max_file_size_bytes: int = Field(
        10_000_000,
        description="Maximum allowed upload file size in bytes. Files exceeding this are rejected with 400.",
    )
    upload_expiry_seconds: int = Field(
        900,
        description="Presigned upload URL expiry duration in seconds.",
    )
    log_level: str = Field(
        "INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR).",
    )


def get_settings() -> Settings:
    """Load settings from environment. In tests, override via FastAPI dependency injection."""
    return Settings(
        app_name=os.environ.get("APP_NAME", "RiskLens API"),
        s3_bucket=os.environ.get("S3_BUCKET", "risklens-submissions-dev"),
        sqs_queue_url=os.environ.get("SQS_QUEUE_URL", ""),
        submissions_table=os.environ.get(
            "SUBMISSIONS_TABLE", os.environ.get("DYNAMODB_TABLE", "")
        ),
        hazards_table=os.environ.get("HAZARDS_TABLE", ""),
        aws_region=os.environ.get("AWS_REGION", "us-east-1"),
        bedrock_model_id=os.environ.get(
            "BEDROCK_MODEL_ID", "eu.anthropic.claude-sonnet-4-6"
        ),
        bedrock_max_input_chars=int(os.environ.get("BEDROCK_MAX_INPUT_CHARS", "8000")),
        max_file_size_bytes=int(os.environ.get("MAX_FILE_SIZE_BYTES", "10000000")),
        upload_expiry_seconds=int(os.environ.get("UPLOAD_EXPIRY_SECONDS", "900")),
        log_level=os.environ.get("LOG_LEVEL", "INFO"),
    )
