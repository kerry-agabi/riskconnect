from __future__ import annotations

import json
from io import BytesIO
from typing import Any

import pytest
from botocore.exceptions import ClientError

from risklens_api.core.errors import NonRetryableError
from risklens_api.schemas.submissions import (
    Address,
    ExtractedData,
    HazardData,
    StormEventCounts,
)
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


class FakeBedrockBody:
    def __init__(self, payload: dict[str, Any]) -> None:
        self._payload = payload

    def read(self) -> bytes:
        return json.dumps(self._payload).encode("utf-8")


class FakeBedrockClient:
    def __init__(self, responses: list[str]) -> None:
        self.responses = responses
        self.requests: list[dict[str, Any]] = []

    def invoke_model(self, **kwargs: Any) -> dict[str, Any]:
        self.requests.append(kwargs)
        text = self.responses.pop(0)
        return {
            "body": FakeBedrockBody({
                "content": [
                    {
                        "type": "text",
                        "text": text,
                    }
                ]
            })
        }


class FakeDynamoTable:
    def __init__(self) -> None:
        self.items: list[dict[str, Any]] = []

    def put_item(self, **kwargs: Any) -> dict[str, Any]:
        self.items.append(kwargs["Item"])
        return {}


class FakeDynamoResource:
    def __init__(self, table: FakeDynamoTable) -> None:
        self.table = table

    def Table(self, table_name: str) -> FakeDynamoTable:  # noqa: N802 - boto3 API
        return self.table


class FailingBedrockClient:
    def invoke_model(self, **kwargs: Any) -> dict[str, Any]:
        raise ClientError(
            {
                "Error": {
                    "Code": "ValidationException",
                    "Message": "Invocation requires an inference profile",
                }
            },
            "InvokeModel",
        )


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


def test_bedrock_json_parser_accepts_fenced_json() -> None:
    client = FakeBedrockClient([
        'Here is the JSON:\n```json\n{"insured_name": "Houston Market"}\n```'
    ])

    result = aws_runtime._invoke_bedrock_json(  # noqa: SLF001
        client,
        "eu.anthropic.claude-sonnet-4-6",
        "Return JSON",
        200,
    )

    assert result == {"insured_name": "Houston Market"}


def test_bedrock_json_repair_prompt_includes_invalid_response() -> None:
    client = FakeBedrockClient([
        "insured_name: Houston Market",
        '{"insured_name": "Houston Market"}',
    ])

    result = aws_runtime._invoke_bedrock_json(  # noqa: SLF001
        client,
        "eu.anthropic.claude-sonnet-4-6",
        "Return JSON",
        200,
    )

    assert result == {"insured_name": "Houston Market"}
    repair_body = json.loads(client.requests[1]["body"])
    repair_text = repair_body["messages"][0]["content"][0]["text"]
    assert "Previous invalid response" in repair_text
    assert "insured_name: Houston Market" in repair_text


def test_bedrock_client_validation_error_surfaces_real_message() -> None:
    with pytest.raises(NonRetryableError, match="inference profile"):
        aws_runtime._invoke_bedrock_json(  # noqa: SLF001
            FailingBedrockClient(),
            "anthropic.claude-sonnet-4-6",
            "Return JSON",
            200,
        )


def test_summary_generation_falls_back_when_bedrock_returns_empty_json(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    table = FakeDynamoTable()
    bedrock = FakeBedrockClient(["", ""])

    monkeypatch.setattr(
        aws_runtime.boto3,
        "resource",
        lambda service_name, **kwargs: FakeDynamoResource(table),
    )
    monkeypatch.setattr(
        aws_runtime.boto3,
        "client",
        lambda service_name, **kwargs: bedrock,
    )
    service = aws_runtime.DynamoSummaryGenerationService(
        table_name="submissions",
        region_name="eu-west-1",
        model_id="eu.anthropic.claude-sonnet-4-6",
        max_output_tokens=500,
    )

    service.generate_summary(
        "SUB-1",
        ExtractedData(
            insured_name="Veridian Light Manufacturing LLC",
            address=Address(
                line1="14350 Victory Blvd",
                city="Los Angeles",
                state="CA",
                postal_code="91401",
                county_fips="06037",
            ),
            industry="Light manufacturing",
            requested_coverage="Commercial Property",
        ),
        HazardData(
            fema_risk_rating="Relatively High",
            top_hazards=["Earthquake", "Wildfire", "Riverine Flooding"],
            recent_disaster_declarations=4,
            storm_event_counts_10yr=StormEventCounts(
                hail=16,
                strong_wind=83,
                flash_flood=21,
            ),
        ),
    )

    assert len(bedrock.requests) == 2
    assert len(table.items) == 1
    item = table.items[0]
    assert item["pk"] == "SUBMISSION#SUB-1"
    assert item["sk"] == "SUMMARY"
    assert item["aiBrief"]["confidence"] == "low"
    assert "model response was not valid JSON" in item["aiBrief"]["executiveSummary"]
