"""Dependency-injection seams for the worker orchestrator.

Defines narrow, typed Protocols for each pipeline stage the worker drives
and for the submission status store. Production implementations wrap AWS
SDK calls (Textract, Bedrock, DynamoDB, S3); tests inject fakes from
``services.fakes``. Keeping these Protocols small keeps the orchestrator
independent of AWS internals and easy to test.
"""

from __future__ import annotations

from typing import Protocol

from risklens_api.core.constants import SubmissionStatus
from risklens_api.schemas.processing import (
    EnrichmentResult,
    FieldExtractionResult,
    TextExtractionResult,
)
from risklens_api.schemas.submissions import Address, DataSource, ExtractedData, HazardData


class StatusStore(Protocol):
    """Read/update seam for submission status, independent of the API service.

    The worker owns status transitions during processing. Implementations
    persist to the same source of truth as the API (DynamoDB) but are
    injected so the worker never reaches into ``SubmissionService`` internals.
    """

    def get_status(self, submission_id: str) -> SubmissionStatus | None:
        """Return the current status, or None if the submission is unknown."""
        ...

    def set_status(
        self,
        submission_id: str,
        status: SubmissionStatus,
        reason: str | None = None,
    ) -> None:
        """Persist a status transition, optionally with a broker-readable reason.

        ``reason`` is stored on the record for terminal states such as
        NEEDS_REVIEW and FAILED and surfaced to brokers via the API.
        """
        ...


class TextExtractionService(Protocol):
    """OCR / text-extraction stage (Textract or local PDF parse)."""

    def extract_text(
        self, submission_id: str, object_key: str
    ) -> TextExtractionResult:
        """Extract document text and return the stored-text artifact location."""
        ...


class FieldExtractionService(Protocol):
    """Structured-field extraction stage (Bedrock)."""

    def extract_fields(
        self, submission_id: str, text_object_key: str
    ) -> FieldExtractionResult:
        """Extract structured submission facts from the previously stored text."""
        ...


class GeocodeService(Protocol):
    """Resolves a US address to a 5-digit county FIPS code.

    The single resolution path for county FIPS during enrichment. Even when the
    extracted address already carries a ``county_fips``, callers route through
    this seam so the lookup strategy stays in one place. Production implements a
    US Census Geocoder HTTP adapter; tests inject a fixture-backed fake.
    """

    def resolve_county_fips(self, address: Address) -> str | None:
        """Return the 5-digit county FIPS for the address, or None if unresolved.

        Returning None (not raising) is the clean "not found" signal; the
        enrichment stage maps it to a NEEDS_REVIEW outcome.
        """
        ...


class HazardRepository(Protocol):
    """Reads pre-aggregated county hazard summaries keyed by 5-digit FIPS.

    Backs the "Worker reads hazard cache by county/FIPS" architecture step.
    Production reads the Terraform-managed S3/DynamoDB hazard cache; tests
    inject a fixture-backed fake. Returns None when no row exists for the FIPS.
    """

    def get_by_fips(self, county_fips: str) -> HazardData | None:
        """Return normalized hazard data for the county, or None if absent."""
        ...


class EnrichmentService(Protocol):
    """Public hazard-data enrichment stage (hazard cache join)."""

    def enrich(
        self, submission_id: str, extracted: ExtractedData
    ) -> EnrichmentResult:
        """Join public hazard data for the extracted insured location.

        Resolves county FIPS via :class:`GeocodeService`, reads the hazard
        cache via :class:`HazardRepository`, and returns an
        :class:`EnrichmentResult`. Geocode or hazard misses produce a
        NEEDS_REVIEW outcome rather than an exception.
        """
        ...


class SummaryGenerationService(Protocol):
    """Underwriting-brief generation stage (Bedrock)."""

    def generate_summary(
        self,
        submission_id: str,
        extracted: ExtractedData,
        hazards: HazardData,
        sources: list[DataSource] | None = None,
    ) -> None:
        """Generate and persist the broker-reviewable triage brief."""
        ...
