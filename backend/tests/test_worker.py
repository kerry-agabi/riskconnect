"""Behavior tests for the worker orchestrator.

Drives the pipeline with fakes only (no AWS). Covers the happy path, the
retryable-failure boundary, and the missing-address NEEDS_REVIEW path.
"""

from __future__ import annotations

import pytest

from risklens_api.core.constants import SubmissionStatus
from risklens_api.core.errors import NonRetryableError, RetryableError
from risklens_api.schemas.processing import (
    EnrichmentOutcome,
    EnrichmentResult,
    ProcessingMessage,
)
from risklens_api.schemas.submissions import Address, ExtractedData
from risklens_api.services.fakes import (
    FakeEnrichmentService,
    FakeFieldExtractionService,
    FakeStatusStore,
    FakeSummaryGenerationService,
    FakeTextExtractionService,
)
from risklens_api.worker.processor import SubmissionProcessor

SUBMISSION_ID = "TEST-WORKER-001"
CORRELATION_ID = "CORR-001"


def _message() -> ProcessingMessage:
    return ProcessingMessage(
        submission_id=SUBMISSION_ID,
        object_key=f"submissions/{SUBMISSION_ID}/raw/test.pdf",
    )


def _build(
    *,
    status_store: FakeStatusStore | None = None,
    text: FakeTextExtractionService | None = None,
    fields: FakeFieldExtractionService | None = None,
    enrichment: FakeEnrichmentService | None = None,
    summary: FakeSummaryGenerationService | None = None,
) -> tuple[SubmissionProcessor, FakeStatusStore, FakeSummaryGenerationService]:
    store = status_store or FakeStatusStore(
        {SUBMISSION_ID: SubmissionStatus.QUEUED}
    )
    summary_service = summary or FakeSummaryGenerationService()
    processor = SubmissionProcessor(
        status_store=store,
        text_extraction=text or FakeTextExtractionService(),
        field_extraction=fields or FakeFieldExtractionService(),
        enrichment=enrichment or FakeEnrichmentService(),
        summary_generation=summary_service,
    )
    return processor, store, summary_service


def test_happy_path_transitions_to_ready() -> None:
    processor, store, summary = _build()

    final = processor.process(_message(), CORRELATION_ID)

    assert final == SubmissionStatus.READY
    transitions = [status for sid, status in store.history if sid == SUBMISSION_ID]
    assert transitions == [
        SubmissionStatus.OCR_RUNNING,
        SubmissionStatus.EXTRACTING,
        SubmissionStatus.ENRICHING,
        SubmissionStatus.GENERATING_SUMMARY,
        SubmissionStatus.READY,
    ]
    assert summary.calls == [SUBMISSION_ID]


def test_retryable_failure_reraises_and_does_not_fail() -> None:
    text = FakeTextExtractionService(error=RetryableError("Textract throttled"))
    processor, store, summary = _build(text=text)

    with pytest.raises(RetryableError):
        processor.process(_message(), CORRELATION_ID)

    # Status must NOT be FAILED; SQS owns retry/exhaustion.
    assert store.get_status(SUBMISSION_ID) != SubmissionStatus.FAILED
    # No reason stored and summary stage never ran.
    assert SUBMISSION_ID not in store.reasons
    assert summary.calls == []


def test_non_retryable_failure_marks_failed_with_reason() -> None:
    text = FakeTextExtractionService(
        error=NonRetryableError("Document is corrupt and cannot be read")
    )
    processor, store, summary = _build(text=text)

    final = processor.process(_message(), CORRELATION_ID)

    assert final == SubmissionStatus.FAILED
    assert store.get_status(SUBMISSION_ID) == SubmissionStatus.FAILED
    assert "corrupt" in store.reasons[SUBMISSION_ID]
    assert summary.calls == []


def test_missing_address_routes_to_needs_review() -> None:
    def no_address() -> ExtractedData:
        return ExtractedData(
            insured_name="Mystery Co",
            address=None,
            industry="Unknown",
        )

    fields = FakeFieldExtractionService(extracted_factory=no_address)
    enrichment = FakeEnrichmentService()
    processor, store, summary = _build(fields=fields, enrichment=enrichment)

    final = processor.process(_message(), CORRELATION_ID)

    assert final == SubmissionStatus.NEEDS_REVIEW
    assert store.get_status(SUBMISSION_ID) == SubmissionStatus.NEEDS_REVIEW
    assert SUBMISSION_ID in store.reasons
    assert "address" in store.reasons[SUBMISSION_ID].lower()
    # Enrichment and summary stages must not run for NEEDS_REVIEW.
    assert enrichment.calls == []
    assert summary.calls == []
    # Ended after EXTRACTING; no ENRICHING/GENERATING_SUMMARY transitions.
    transitions = [status for sid, status in store.history if sid == SUBMISSION_ID]
    assert transitions == [
        SubmissionStatus.OCR_RUNNING,
        SubmissionStatus.EXTRACTING,
        SubmissionStatus.NEEDS_REVIEW,
    ]


def test_address_present_but_no_line1_routes_to_needs_review() -> None:
    def partial_address() -> ExtractedData:
        return ExtractedData(
            insured_name="Partial Co",
            address=Address(city="Los Angeles", state="CA"),
        )

    fields = FakeFieldExtractionService(extracted_factory=partial_address)
    processor, store, summary = _build(fields=fields)

    final = processor.process(_message(), CORRELATION_ID)

    assert final == SubmissionStatus.NEEDS_REVIEW
    assert summary.calls == []


def test_enrichment_needs_review_routes_to_needs_review() -> None:
    # Enrichment could not resolve a county / hazard data; it signals review
    # via the typed outcome rather than raising.
    review_reason = "No county hazard data available; broker review required."

    def review_result() -> EnrichmentResult:
        return EnrichmentResult(
            outcome=EnrichmentOutcome.NEEDS_REVIEW,
            county_fips=None,
            hazards=None,
            review_reason=review_reason,
        )

    enrichment = FakeEnrichmentService(result_factory=review_result)
    processor, store, summary = _build(enrichment=enrichment)

    final = processor.process(_message(), CORRELATION_ID)

    assert final == SubmissionStatus.NEEDS_REVIEW
    assert store.get_status(SUBMISSION_ID) == SubmissionStatus.NEEDS_REVIEW
    assert store.reasons[SUBMISSION_ID] == review_reason
    # Enrichment ran but summary generation must not.
    assert enrichment.calls == [SUBMISSION_ID]
    assert summary.calls == []
    # Reached ENRICHING but never GENERATING_SUMMARY.
    transitions = [status for sid, status in store.history if sid == SUBMISSION_ID]
    assert transitions == [
        SubmissionStatus.OCR_RUNNING,
        SubmissionStatus.EXTRACTING,
        SubmissionStatus.ENRICHING,
        SubmissionStatus.NEEDS_REVIEW,
    ]


def test_redelivered_terminal_message_is_noop() -> None:
    # Submission already READY (e.g. duplicate SQS delivery).
    store = FakeStatusStore({SUBMISSION_ID: SubmissionStatus.READY})
    text = FakeTextExtractionService()
    processor, store, summary = _build(status_store=store, text=text)

    final = processor.process(_message(), CORRELATION_ID)

    assert final == SubmissionStatus.READY
    # No pipeline work and no new transitions recorded.
    assert text.calls == []
    assert summary.calls == []
    assert store.history == []
