from __future__ import annotations

from io import BytesIO
from typing import Any

import pytest

from risklens_api.core.errors import NonRetryableError
from risklens_api.services import aws_runtime


class FakeS3Client:
    def __init__(self, *, content_type: str, body: bytes = b"") -> None:
        self.content_type = content_type
        self.body = body
        self.puts: list[dict[str, Any]] = []

    def head_object(self, **kwargs: Any) -> dict[str, Any]:
        return {"ContentType": self.content_type}

    def get_object(self, **kwargs: Any) -> dict[str, Any]:
        return {"Body": BytesIO(self.body)}

    def put_object(self, **kwargs: Any) -> dict[str, Any]:
        self.puts.append(kwargs)
        return {}


class FakeTextractClient:
    def __init__(self, *, status: str = "SUCCEEDED", status_message: str | None = None) -> None:
        self.status = status
        self.status_message = status_message
        self.started = False

    def start_document_text_detection(self, **kwargs: Any) -> dict[str, str]:
        self.started = True
        return {"JobId": "job-1"}

    def get_document_text_detection(self, **kwargs: Any) -> dict[str, Any]:
        response: dict[str, Any] = {"JobStatus": self.status}
        if self.status_message:
            response["StatusMessage"] = self.status_message
        if self.status == "SUCCEEDED":
            response["Blocks"] = [{"BlockType": "LINE", "Text": "Extracted line"}]
        return response


def _patch_boto3_clients(
    monkeypatch: pytest.MonkeyPatch,
    *,
    s3: FakeS3Client,
    textract: FakeTextractClient,
) -> None:
    def fake_client(service_name: str, **kwargs: Any) -> Any:
        if service_name == "s3":
            return s3
        if service_name == "textract":
            return textract
        raise AssertionError(f"Unexpected boto3 client: {service_name}")

    monkeypatch.setattr(aws_runtime.boto3, "client", fake_client)


def test_text_extraction_reads_plain_text_without_textract(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    s3 = FakeS3Client(
        content_type="text/plain; charset=utf-8",
        body=b"insured: Houston Market\naddress: 100 Main St, Houston, TX",
    )
    textract = FakeTextractClient()
    _patch_boto3_clients(monkeypatch, s3=s3, textract=textract)
    service = aws_runtime.TextractTextExtractionService("bucket", "eu-west-1")

    result = service.extract_text("SUB-1", "submissions/SUB-1/raw/submission")

    assert not textract.started
    assert result.text_object_key == "submissions/SUB-1/text/extracted.txt"
    assert result.character_count == len(
        "insured: Houston Market\naddress: 100 Main St, Houston, TX"
    )
    assert s3.puts[0]["Body"] == b"insured: Houston Market\naddress: 100 Main St, Houston, TX"


def test_text_extraction_reports_textract_failure_message(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    s3 = FakeS3Client(content_type="application/pdf")
    textract = FakeTextractClient(
        status="FAILED",
        status_message="Unsupported document format",
    )
    _patch_boto3_clients(monkeypatch, s3=s3, textract=textract)
    service = aws_runtime.TextractTextExtractionService(
        "bucket",
        "eu-west-1",
        poll_seconds=0,
    )

    with pytest.raises(NonRetryableError, match="Unsupported document format"):
        service.extract_text("SUB-1", "submissions/SUB-1/raw/submission.pdf")

    assert textract.started
