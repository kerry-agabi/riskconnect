"""Tests for Pydantic schema serialization."""

from __future__ import annotations

from datetime import datetime, timezone

from risklens_api.core.constants import SubmissionStatus
from risklens_api.schemas.submissions import (
    FileInfo,
    SubmissionStatusResponse,
    UploadUrlRequest,
    UploadUrlResponse,
)


def test_upload_url_request_from_camel_case() -> None:
    req = UploadUrlRequest.model_validate(
        {"fileName": "doc.pdf", "contentType": "application/pdf", "fileSizeBytes": 500}
    )
    assert req.file_name == "doc.pdf"
    assert req.content_type == "application/pdf"
    assert req.file_size_bytes == 500


def test_upload_url_response_serializes_camel_case() -> None:
    resp = UploadUrlResponse(
        submission_id="ABC123",
        upload_url="https://example.com",
        object_key="submissions/ABC123/raw/doc.pdf",
        expires_in_seconds=900,
        max_file_size_bytes=10_000_000,
    )
    data = resp.model_dump(by_alias=True)
    assert "submissionId" in data
    assert "uploadUrl" in data
    assert "objectKey" in data
    assert "expiresInSeconds" in data
    assert "maxFileSizeBytes" in data


def test_submission_status_response_serializes() -> None:
    now = datetime.now(timezone.utc)
    resp = SubmissionStatusResponse(
        submission_id="X1",
        status=SubmissionStatus.UPLOADED,
        created_at=now,
        updated_at=now,
        file=FileInfo(file_name="f.pdf", content_type="application/pdf"),
    )
    data = resp.model_dump(by_alias=True)
    assert data["submissionId"] == "X1"
    assert data["status"] == "UPLOADED"
    assert data["file"]["fileName"] == "f.pdf"
