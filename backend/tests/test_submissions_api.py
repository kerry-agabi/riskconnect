"""Tests for submission API endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient

from risklens_api.core.constants import SubmissionStatus
from risklens_api.services.fakes import FakeQueueService
from risklens_api.services.submission_service import SubmissionService


# ---------------------------------------------------------------------------
# POST /submissions/upload-url -- success paths
# ---------------------------------------------------------------------------


def test_create_upload_url(client: TestClient) -> None:
    response = client.post(
        "/api/submissions/upload-url",
        json={"fileName": "test.pdf", "contentType": "application/pdf", "fileSizeBytes": 1000},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["submissionId"] == "TEST-ID-001"
    assert "uploadUrl" in data
    assert data["objectKey"] == "submissions/TEST-ID-001/raw/test.pdf"
    assert data["expiresInSeconds"] == 900
    assert data["maxFileSizeBytes"] == 10_000_000


def test_create_upload_url_png(client: TestClient) -> None:
    response = client.post(
        "/api/submissions/upload-url",
        json={"fileName": "scan.png", "contentType": "image/png", "fileSizeBytes": 500},
    )
    assert response.status_code == 201
    assert response.json()["objectKey"] == "submissions/TEST-ID-001/raw/scan.png"


def test_create_upload_url_jpeg(client: TestClient) -> None:
    response = client.post(
        "/api/submissions/upload-url",
        json={"fileName": "photo.jpg", "contentType": "image/jpeg", "fileSizeBytes": 800},
    )
    assert response.status_code == 201


def test_create_upload_url_text_plain(client: TestClient) -> None:
    response = client.post(
        "/api/submissions/upload-url",
        json={"fileName": "notes.txt", "contentType": "text/plain", "fileSizeBytes": 200},
    )
    assert response.status_code == 201


# ---------------------------------------------------------------------------
# POST /submissions/upload-url -- validation failures
# ---------------------------------------------------------------------------


def test_create_upload_url_invalid_content_type(client: TestClient) -> None:
    response = client.post(
        "/api/submissions/upload-url",
        json={"fileName": "test.zip", "contentType": "application/zip", "fileSizeBytes": 1000},
    )
    assert response.status_code == 400
    assert "Unsupported content type" in response.json()["detail"]


def test_create_upload_url_file_too_large(client: TestClient) -> None:
    response = client.post(
        "/api/submissions/upload-url",
        json={
            "fileName": "big.pdf",
            "contentType": "application/pdf",
            "fileSizeBytes": 99_000_000,
        },
    )
    assert response.status_code == 400
    assert "exceeds maximum" in response.json()["detail"]


def test_create_upload_url_missing_fields(client: TestClient) -> None:
    """Missing required fields should return 422 Unprocessable Entity."""
    response = client.post(
        "/api/submissions/upload-url",
        json={"fileName": "test.pdf"},
    )
    assert response.status_code == 422


def test_create_upload_url_empty_body(client: TestClient) -> None:
    """Empty JSON body should return 422."""
    response = client.post(
        "/api/submissions/upload-url",
        json={},
    )
    assert response.status_code == 422


def test_create_upload_url_zero_size(client: TestClient) -> None:
    """File size must be > 0."""
    response = client.post(
        "/api/submissions/upload-url",
        json={"fileName": "test.pdf", "contentType": "application/pdf", "fileSizeBytes": 0},
    )
    assert response.status_code == 422


def test_create_upload_url_negative_size(client: TestClient) -> None:
    """Negative file size should fail validation."""
    response = client.post(
        "/api/submissions/upload-url",
        json={"fileName": "test.pdf", "contentType": "application/pdf", "fileSizeBytes": -1},
    )
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# POST /submissions/{submissionId}/start -- success and idempotency
# ---------------------------------------------------------------------------


def test_start_processing(client: TestClient) -> None:
    client.post(
        "/api/submissions/upload-url",
        json={"fileName": "test.pdf", "contentType": "application/pdf", "fileSizeBytes": 1000},
    )

    response = client.post(
        "/api/submissions/TEST-ID-001/start",
        json={"objectKey": "submissions/TEST-ID-001/raw/test.pdf"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["submissionId"] == "TEST-ID-001"
    assert data["status"] == "QUEUED"


def test_start_processing_idempotent(
    client: TestClient,
    fake_queue: FakeQueueService,
) -> None:
    """Calling start twice should not re-queue and should not error."""
    client.post(
        "/api/submissions/upload-url",
        json={"fileName": "test.pdf", "contentType": "application/pdf", "fileSizeBytes": 1000},
    )

    # First start
    resp1 = client.post(
        "/api/submissions/TEST-ID-001/start",
        json={"objectKey": "submissions/TEST-ID-001/raw/test.pdf"},
    )
    assert resp1.status_code == 200
    assert resp1.json()["status"] == "QUEUED"

    # Second start -- idempotent, no re-queue
    resp2 = client.post(
        "/api/submissions/TEST-ID-001/start",
        json={"objectKey": "submissions/TEST-ID-001/raw/test.pdf"},
    )
    assert resp2.status_code == 200
    assert resp2.json()["status"] == "QUEUED"

    # Queue should only have one message
    assert len(fake_queue.messages) == 1


def test_start_processing_idempotent_after_progress(
    client: TestClient,
    submission_service: SubmissionService,
    fake_queue: FakeQueueService,
) -> None:
    """Start on a submission that has progressed past QUEUED should not re-queue."""
    client.post(
        "/api/submissions/upload-url",
        json={"fileName": "test.pdf", "contentType": "application/pdf", "fileSizeBytes": 1000},
    )

    # Start processing
    client.post(
        "/api/submissions/TEST-ID-001/start",
        json={"objectKey": "submissions/TEST-ID-001/raw/test.pdf"},
    )

    # Simulate worker moving status forward
    submission_service._submissions["TEST-ID-001"].status = SubmissionStatus.OCR_RUNNING

    # Re-start should not re-queue
    resp = client.post(
        "/api/submissions/TEST-ID-001/start",
        json={"objectKey": "submissions/TEST-ID-001/raw/test.pdf"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "OCR_RUNNING"
    assert len(fake_queue.messages) == 1  # still only one message


def test_start_processing_not_found(client: TestClient) -> None:
    response = client.post(
        "/api/submissions/NONEXISTENT/start",
        json={"objectKey": "submissions/NONEXISTENT/raw/test.pdf"},
    )
    assert response.status_code == 404


def test_start_processing_missing_body(client: TestClient) -> None:
    """Missing objectKey should return 422."""
    client.post(
        "/api/submissions/upload-url",
        json={"fileName": "test.pdf", "contentType": "application/pdf", "fileSizeBytes": 1000},
    )
    response = client.post(
        "/api/submissions/TEST-ID-001/start",
        json={},
    )
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# GET /submissions/{submissionId} -- status queries
# ---------------------------------------------------------------------------


def test_get_submission_status(client: TestClient) -> None:
    client.post(
        "/api/submissions/upload-url",
        json={"fileName": "test.pdf", "contentType": "application/pdf", "fileSizeBytes": 1000},
    )

    response = client.get("/api/submissions/TEST-ID-001")
    assert response.status_code == 200
    data = response.json()
    assert data["submissionId"] == "TEST-ID-001"
    assert data["status"] == "UPLOADED"
    assert data["file"]["fileName"] == "test.pdf"
    assert data["file"]["contentType"] == "application/pdf"
    assert "createdAt" in data
    assert "updatedAt" in data
    assert data["progress"] is None
    assert data["error"] is None


def test_get_submission_status_after_start(client: TestClient) -> None:
    """After starting processing, status should be QUEUED."""
    client.post(
        "/api/submissions/upload-url",
        json={"fileName": "test.pdf", "contentType": "application/pdf", "fileSizeBytes": 1000},
    )
    client.post(
        "/api/submissions/TEST-ID-001/start",
        json={"objectKey": "submissions/TEST-ID-001/raw/test.pdf"},
    )

    response = client.get("/api/submissions/TEST-ID-001")
    assert response.status_code == 200
    assert response.json()["status"] == "QUEUED"


def test_get_submission_not_found(client: TestClient) -> None:
    response = client.get("/api/submissions/NONEXISTENT")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# GET /submissions/{submissionId}/summary
# ---------------------------------------------------------------------------


def test_get_summary_not_ready(client: TestClient) -> None:
    client.post(
        "/api/submissions/upload-url",
        json={"fileName": "test.pdf", "contentType": "application/pdf", "fileSizeBytes": 1000},
    )

    response = client.get("/api/submissions/TEST-ID-001/summary")
    assert response.status_code == 409
    assert "not available" in response.json()["detail"]


def test_get_summary_ready(
    client: TestClient,
    submission_service: SubmissionService,
) -> None:
    client.post(
        "/api/submissions/upload-url",
        json={"fileName": "test.pdf", "contentType": "application/pdf", "fileSizeBytes": 1000},
    )
    # Force status to READY for testing
    submission_service._submissions["TEST-ID-001"].status = SubmissionStatus.READY

    response = client.get("/api/submissions/TEST-ID-001/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["submissionId"] == "TEST-ID-001"
    assert data["status"] == "READY"


# ---------------------------------------------------------------------------
# GET /submissions -- list with filter and pagination
# ---------------------------------------------------------------------------


def test_list_submissions_empty(client: TestClient) -> None:
    response = client.get("/api/submissions")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["nextToken"] is None


def test_list_submissions_with_items(client: TestClient) -> None:
    client.post(
        "/api/submissions/upload-url",
        json={"fileName": "test.pdf", "contentType": "application/pdf", "fileSizeBytes": 1000},
    )

    response = client.get("/api/submissions")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["submissionId"] == "TEST-ID-001"


def test_list_submissions_status_filter(
    client: TestClient,
    submission_service: SubmissionService,
) -> None:
    """Filtering by status should return only matching submissions."""
    client.post(
        "/api/submissions/upload-url",
        json={"fileName": "test.pdf", "contentType": "application/pdf", "fileSizeBytes": 1000},
    )

    # With status=UPLOADED we should get the submission
    response_uploaded = client.get("/api/submissions?status=UPLOADED")
    assert response_uploaded.status_code == 200
    assert len(response_uploaded.json()["items"]) == 1

    # With status=QUEUED we should get nothing (submission is still UPLOADED)
    response_queued = client.get("/api/submissions?status=QUEUED")
    assert response_queued.status_code == 200
    assert len(response_queued.json()["items"]) == 0


def test_list_submissions_limit(
    client: TestClient,
    submission_service: SubmissionService,
) -> None:
    """Limit parameter should cap the number of returned items."""
    from risklens_api.services.submission_service import SubmissionRecord

    for i in range(5):
        rec = SubmissionRecord(
            submission_id=f"ID-{i:03d}",
            file_name=f"file{i}.pdf",
            content_type="application/pdf",
            object_key=f"submissions/ID-{i:03d}/raw/file{i}.pdf",
            file_size_bytes=1000,
        )
        submission_service._submissions[rec.submission_id] = rec

    response = client.get("/api/submissions?limit=3")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 3


def test_list_submissions_pagination(
    client: TestClient,
    submission_service: SubmissionService,
) -> None:
    """Pagination should return a nextToken when there are more items."""
    from datetime import datetime, timedelta, timezone

    from risklens_api.services.submission_service import SubmissionRecord

    base_time = datetime(2026, 1, 1, tzinfo=timezone.utc)
    for i in range(5):
        rec = SubmissionRecord(
            submission_id=f"PAGE-{i:03d}",
            file_name=f"file{i}.pdf",
            content_type="application/pdf",
            object_key=f"submissions/PAGE-{i:03d}/raw/file{i}.pdf",
            file_size_bytes=1000,
        )
        # Ensure deterministic ordering
        rec.created_at = base_time + timedelta(minutes=i)
        rec.updated_at = rec.created_at
        submission_service._submissions[rec.submission_id] = rec

    # Request limit=2, should get nextToken because 5 > 2
    response = client.get("/api/submissions?limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["nextToken"] is not None

    # Use nextToken for the next page
    next_token = data["nextToken"]
    response2 = client.get(f"/api/submissions?limit=2&nextToken={next_token}")
    assert response2.status_code == 200
    data2 = response2.json()
    assert len(data2["items"]) == 2
    # Items should be different from the first page
    first_ids = {item["submissionId"] for item in data["items"]}
    second_ids = {item["submissionId"] for item in data2["items"]}
    assert first_ids.isdisjoint(second_ids)


def test_list_submissions_limit_exceeds_max(client: TestClient) -> None:
    """Requesting limit > MAX_LIST_LIMIT (100) should return 422."""
    response = client.get("/api/submissions?limit=101")
    assert response.status_code == 422
