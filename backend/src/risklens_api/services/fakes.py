"""Fake service implementations for local development and testing."""

from __future__ import annotations


class FakeStorageService:
    """In-memory fake for S3 presigned URL generation."""

    def __init__(self) -> None:
        self.calls: list[dict[str, str | int]] = []

    def generate_presigned_upload_url(
        self,
        bucket: str,
        key: str,
        content_type: str,
        expires_in: int,
    ) -> str:
        self.calls.append({
            "bucket": bucket,
            "key": key,
            "content_type": content_type,
        })
        return f"https://fake-s3.example.com/{bucket}/{key}?expires={expires_in}"


class FakeQueueService:
    """In-memory fake for SQS message sending."""

    def __init__(self) -> None:
        self.messages: list[dict[str, str]] = []

    def send_processing_message(self, submission_id: str, object_key: str) -> None:
        self.messages.append({
            "submission_id": submission_id,
            "object_key": object_key,
        })
