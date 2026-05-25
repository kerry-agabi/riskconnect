"""Fake service implementations for local development and testing."""

from __future__ import annotations

from typing import Callable

from risklens_api.core.constants import SubmissionStatus
from risklens_api.schemas.processing import (
    EnrichmentOutcome,
    EnrichmentResult,
    FieldExtractionResult,
    TextExtractionResult,
)
from risklens_api.schemas.submissions import (
    Address,
    DataSource,
    ExtractedData,
    HazardData,
)


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


# ---------------------------------------------------------------------------
# Worker pipeline fakes
# ---------------------------------------------------------------------------


class FakeStatusStore:
    """In-memory fake for the worker status store.

    Records the ordered history of every status transition so tests can
    assert the exact transition sequence, and stores the latest broker-readable
    reason for terminal states.
    """

    def __init__(self, initial: dict[str, SubmissionStatus] | None = None) -> None:
        self.statuses: dict[str, SubmissionStatus] = dict(initial or {})
        self.reasons: dict[str, str] = {}
        self.history: list[tuple[str, SubmissionStatus]] = []

    def get_status(self, submission_id: str) -> SubmissionStatus | None:
        return self.statuses.get(submission_id)

    def set_status(
        self,
        submission_id: str,
        status: SubmissionStatus,
        reason: str | None = None,
    ) -> None:
        self.statuses[submission_id] = status
        self.history.append((submission_id, status))
        if reason is not None:
            self.reasons[submission_id] = reason


class FakeTextExtractionService:
    """Fake OCR stage. Optionally raises an injected error for failure tests."""

    def __init__(self, error: Exception | None = None) -> None:
        self.error = error
        self.calls: list[str] = []

    def extract_text(
        self, submission_id: str, object_key: str
    ) -> TextExtractionResult:
        self.calls.append(submission_id)
        if self.error is not None:
            raise self.error
        return TextExtractionResult(
            text_object_key=f"submissions/{submission_id}/text/extracted.txt",
            character_count=1200,
        )


class FakeFieldExtractionService:
    """Fake structured-field extraction stage.

    ``extracted_factory`` lets a test control the returned facts (e.g. to omit
    the address for the NEEDS_REVIEW path). ``error`` injects a failure.
    """

    def __init__(
        self,
        extracted_factory: Callable[[], ExtractedData] | None = None,
        error: Exception | None = None,
    ) -> None:
        self.error = error
        self.calls: list[str] = []
        self._extracted_factory = extracted_factory or _default_extracted

    def extract_fields(
        self, submission_id: str, text_object_key: str
    ) -> FieldExtractionResult:
        self.calls.append(submission_id)
        if self.error is not None:
            raise self.error
        return FieldExtractionResult(extracted=self._extracted_factory())


class FakeEnrichmentService:
    """Fake hazard-enrichment stage.

    ``result_factory`` lets a test control the returned :class:`EnrichmentResult`
    (e.g. to exercise the NEEDS_REVIEW enrichment path in the orchestrator).
    ``error`` injects a failure.
    """

    def __init__(
        self,
        result_factory: Callable[[], EnrichmentResult] | None = None,
        error: Exception | None = None,
    ) -> None:
        self.error = error
        self.calls: list[str] = []
        self._result_factory = result_factory or _default_enrichment

    def enrich(
        self, submission_id: str, extracted: ExtractedData
    ) -> EnrichmentResult:
        self.calls.append(submission_id)
        if self.error is not None:
            raise self.error
        return self._result_factory()


class FakeSummaryGenerationService:
    """Fake summary-generation stage. Records whether it ran."""

    def __init__(self, error: Exception | None = None) -> None:
        self.error = error
        self.calls: list[str] = []

    def generate_summary(
        self,
        submission_id: str,
        extracted: ExtractedData,
        hazards: HazardData,
        sources: list[DataSource] | None = None,
    ) -> None:
        self.calls.append(submission_id)
        if self.error is not None:
            raise self.error


def _default_enrichment() -> EnrichmentResult:
    """Build a populated, ENRICHED result for happy-path worker tests."""
    return EnrichmentResult(
        outcome=EnrichmentOutcome.ENRICHED,
        county_fips="06037",
        hazards=HazardData(
            fema_risk_rating="Relatively High",
            top_hazards=["Earthquake", "Wildfire"],
            recent_disaster_declarations=4,
            storm_event_counts_10yr=None,
        ),
        sources=[
            DataSource(
                name="FEMA National Risk Index",
                url="https://hazards.fema.gov/nri/data-resources",
            ),
        ],
    )


def _default_extracted() -> ExtractedData:
    """Build a fully-populated extraction result for happy-path tests."""
    return ExtractedData(
        insured_name="Example Manufacturing LLC",
        address=Address(
            line1="100 Example Ave",
            city="Los Angeles",
            state="CA",
            postal_code="90012",
            county_fips="06037",
        ),
        industry="Light manufacturing",
        requested_coverage="Commercial property",
        limits=None,
    )
