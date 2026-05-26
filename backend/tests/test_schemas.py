"""Tests for Pydantic schema serialization."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from risklens_api.core.constants import SubmissionStatus
from risklens_api.schemas.submissions import (
    AIBrief,
    ExtractedData,
    FileInfo,
    HazardData,
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


def test_summary_submodels_accept_camel_case_from_dynamo() -> None:
    extracted = ExtractedData.model_validate(
        {
            "insuredName": "Veridian Light Manufacturing LLC",
            "address": {
                "line1": "14350 Victory Blvd",
                "city": "Los Angeles",
                "state": "CA",
                "postalCode": "91401",
                "countyFips": "06037",
            },
            "requestedCoverage": "Commercial Property",
            "limits": {"building": 6500000, "businessPersonalProperty": 1750000},
            "missingFields": [],
        }
    )
    hazards = HazardData.model_validate(
        {
            "femaRiskRating": "Relatively High",
            "topHazards": ["Earthquake", "Wildfire"],
            "recentDisasterDeclarations": 4,
            "stormEventCounts10Yr": {
                "hail": 16,
                "strongWind": 83,
                "flashFlood": 21,
            },
        }
    )
    brief = AIBrief.model_validate(
        {
            "executiveSummary": "Structured fallback summary.",
            "riskFlags": ["County hazard profile: Relatively High."],
            "questionsForBroker": ["Confirm address."],
            "confidence": "low",
        }
    )

    assert extracted.insured_name == "Veridian Light Manufacturing LLC"
    assert extracted.address is not None
    assert extracted.address.postal_code == "91401"
    assert extracted.limits is not None
    assert extracted.limits.business_personal_property == 1750000
    assert hazards.storm_event_counts_10yr is not None
    assert hazards.storm_event_counts_10yr.strong_wind == 83
    assert brief.executive_summary == "Structured fallback summary."


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (0.38, "medium"),
        (0.9, "high"),
        (0.1, "low"),
        (0.66, "high"),
        (0.33, "medium"),
        ("high", "high"),
        (None, None),
    ],
)
def test_ai_brief_coerces_numeric_confidence(raw, expected):
    brief = AIBrief.model_validate({"confidence": raw})
    assert brief.confidence == expected
