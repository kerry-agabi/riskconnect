"""Worker orchestrator that drives a submission through the processing pipeline.

Given a :class:`ProcessingMessage`, advances a submission through the explicit
status sequence:

    OCR_RUNNING -> EXTRACTING -> ENRICHING -> GENERATING_SUMMARY -> READY

Terminal outcomes:

- ``READY``        - all stages succeeded.
- ``NEEDS_REVIEW`` - document processed but a required business field
                     (currently the property address) is missing. This is a
                     normal outcome, not an error: a broker-readable reason is
                     stored and no summary is generated.
- ``FAILED``       - a NonRetryableError (validation/permanent failure) was
                     raised by a stage. The worker stores a broker-readable
                     reason and stops.

Failure boundary (see ``core.errors``):

- ``RetryableError`` is re-raised unchanged. The worker does NOT set FAILED;
  it lets the SQS redrive policy retry the message and, after the configured
  attempts, route it to the DLQ. This is the "retries exhausted" boundary -
  it is owned by SQS, not by this orchestrator.
- ``NonRetryableError`` is caught and mapped to terminal FAILED here, because
  retrying the same message cannot succeed.

Idempotency: a re-delivered SQS message for a submission already in a terminal
state (READY / NEEDS_REVIEW / FAILED) is a no-op, so duplicate delivery cannot
corrupt a completed submission.
"""

from __future__ import annotations

from risklens_api.core.constants import SubmissionStatus
from risklens_api.core.errors import NonRetryableError, RetryableError
from risklens_api.core.logging import get_logger
from risklens_api.schemas.processing import EnrichmentOutcome, ProcessingMessage
from risklens_api.worker.protocols import (
    EnrichmentService,
    FieldExtractionService,
    StatusStore,
    SummaryGenerationService,
    TextExtractionService,
)

_COMPONENT = "worker"

# Statuses that mean processing is complete; re-delivery must not re-run.
_TERMINAL_STATUSES = frozenset(
    {
        SubmissionStatus.READY,
        SubmissionStatus.NEEDS_REVIEW,
        SubmissionStatus.FAILED,
    }
)

# Required business fields that must be present to produce a usable brief.
# Missing any of these routes the submission to NEEDS_REVIEW.
_MISSING_ADDRESS_REASON = (
    "Property address could not be extracted from the submission document. "
    "Broker review required to supply the insured location."
)


class SubmissionProcessor:
    """Orchestrates the async processing pipeline for a single submission.

    All collaborators are injected so the orchestrator can be driven entirely
    by fakes in tests and by AWS-backed services in production.
    """

    def __init__(
        self,
        status_store: StatusStore,
        text_extraction: TextExtractionService,
        field_extraction: FieldExtractionService,
        enrichment: EnrichmentService,
        summary_generation: SummaryGenerationService,
    ) -> None:
        self._status_store = status_store
        self._text_extraction = text_extraction
        self._field_extraction = field_extraction
        self._enrichment = enrichment
        self._summary_generation = summary_generation
        self._logger = get_logger()

    def process(self, message: ProcessingMessage, correlation_id: str) -> SubmissionStatus:
        """Drive one submission through the pipeline and return its final status.

        Re-raises :class:`RetryableError` so SQS retries the message. Maps
        :class:`NonRetryableError` to terminal FAILED. Missing required fields
        produce terminal NEEDS_REVIEW.
        """
        submission_id = message.submission_id

        current = self._status_store.get_status(submission_id)
        if current in _TERMINAL_STATUSES:
            # Idempotent guard: a re-delivered message for a completed
            # submission must not re-run the pipeline or overwrite results.
            self._logger.info(
                "Skipping already-terminal submission",
                extra={
                    "component": _COMPONENT,
                    "correlation_id": correlation_id,
                    "submission_id": submission_id,
                    "status": current,
                },
            )
            return current  # type: ignore[return-value]

        try:
            # --- OCR / text extraction ---
            self._transition(submission_id, SubmissionStatus.OCR_RUNNING, correlation_id)
            text_result = self._text_extraction.extract_text(
                submission_id, message.object_key
            )

            # --- Structured field extraction ---
            self._transition(submission_id, SubmissionStatus.EXTRACTING, correlation_id)
            field_result = self._field_extraction.extract_fields(
                submission_id, text_result.text_object_key
            )
            extracted = field_result.extracted

            # Missing required business data is a normal terminal outcome,
            # not an exception. Stop before enrichment/summary generation.
            if not self._has_required_fields(extracted):
                self._status_store.set_status(
                    submission_id,
                    SubmissionStatus.NEEDS_REVIEW,
                    reason=_MISSING_ADDRESS_REASON,
                )
                self._logger.info(
                    "Submission requires broker review",
                    extra={
                        "component": _COMPONENT,
                        "correlation_id": correlation_id,
                        "submission_id": submission_id,
                        "status": SubmissionStatus.NEEDS_REVIEW,
                    },
                )
                return SubmissionStatus.NEEDS_REVIEW

            # --- Hazard enrichment ---
            self._transition(submission_id, SubmissionStatus.ENRICHING, correlation_id)
            enrichment_result = self._enrichment.enrich(submission_id, extracted)

            # Enrichment that cannot resolve a county or find hazard data is a
            # normal terminal outcome, not an exception. Mirror the missing-
            # address gate: store the broker-readable reason and stop before
            # summary generation.
            if enrichment_result.outcome is EnrichmentOutcome.NEEDS_REVIEW:
                self._status_store.set_status(
                    submission_id,
                    SubmissionStatus.NEEDS_REVIEW,
                    reason=enrichment_result.review_reason,
                )
                self._logger.info(
                    "Submission requires broker review",
                    extra={
                        "component": _COMPONENT,
                        "correlation_id": correlation_id,
                        "submission_id": submission_id,
                        "status": SubmissionStatus.NEEDS_REVIEW,
                    },
                )
                return SubmissionStatus.NEEDS_REVIEW

            # --- Summary generation ---
            # Invariant: an ENRICHED outcome always carries hazard data.
            hazards = enrichment_result.hazards
            assert hazards is not None  # noqa: S101 - guards the ENRICHED invariant
            self._transition(
                submission_id, SubmissionStatus.GENERATING_SUMMARY, correlation_id
            )
            self._summary_generation.generate_summary(
                submission_id, extracted, hazards, enrichment_result.sources
            )

            # --- Done ---
            self._transition(submission_id, SubmissionStatus.READY, correlation_id)
            return SubmissionStatus.READY

        except RetryableError:
            # Do NOT set FAILED. Re-raise so the SQS redrive policy retries
            # and, once attempts are exhausted, routes the message to the DLQ.
            self._logger.warning(
                "Retryable error during processing; leaving for SQS retry",
                extra={
                    "component": _COMPONENT,
                    "correlation_id": correlation_id,
                    "submission_id": submission_id,
                    "status": self._status_store.get_status(submission_id),
                },
                exc_info=True,
            )
            raise

        except NonRetryableError as exc:
            # Permanent failure: retrying cannot help. Mark terminal FAILED
            # with a broker-readable reason.
            self._status_store.set_status(
                submission_id, SubmissionStatus.FAILED, reason=str(exc)
            )
            self._logger.error(
                "Non-retryable error during processing; marking FAILED",
                extra={
                    "component": _COMPONENT,
                    "correlation_id": correlation_id,
                    "submission_id": submission_id,
                    "status": SubmissionStatus.FAILED,
                },
                exc_info=True,
            )
            return SubmissionStatus.FAILED

    def _transition(
        self,
        submission_id: str,
        status: SubmissionStatus,
        correlation_id: str,
    ) -> None:
        """Persist a status transition and emit one structured log line."""
        self._status_store.set_status(submission_id, status)
        self._logger.info(
            "Submission status transition",
            extra={
                "component": _COMPONENT,
                "correlation_id": correlation_id,
                "submission_id": submission_id,
                "status": status,
            },
        )

    @staticmethod
    def _has_required_fields(extracted) -> bool:  # type: ignore[no-untyped-def]
        """Return True only if the minimum business data for a brief is present.

        Currently requires a property address with at least a street line.
        Occupancy/industry can be expanded here as enrichment matures.
        """
        address = extracted.address
        return address is not None and bool(address.line1)
