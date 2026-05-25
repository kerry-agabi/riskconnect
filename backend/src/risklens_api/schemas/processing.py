"""Pydantic models for worker processing messages and pipeline-stage results.

These models define the contract between the SQS queue, the worker
orchestrator, and the injectable pipeline-stage services. They are internal
(not part of the public API contract) but follow the same typing and
documentation standards: every model has a class docstring and every field
has a description.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from risklens_api.schemas.submissions import DataSource, ExtractedData, HazardData


class ProcessingMessage(BaseModel):
    """Work item delivered to the worker for a single submission.

    Corresponds to the SQS message body produced by the API Lambda when a
    submission moves to QUEUED. The worker uses these fields to load the
    raw document and drive the submission through the processing pipeline.
    """

    submission_id: str = Field(
        description="Identifier of the submission to process.",
    )
    object_key: str = Field(
        description="S3 object key of the raw uploaded document to process.",
    )

    model_config = ConfigDict(extra="forbid")


class TextExtractionResult(BaseModel):
    """Result of the OCR / text-extraction stage.

    Carries the location of the extracted text artifact rather than the text
    itself, so the worker never holds or logs full document content.
    """

    text_object_key: str = Field(
        description="S3 object key where the extracted plain text artifact is stored.",
    )
    character_count: int = Field(
        ge=0,
        description="Number of characters extracted, used for coarse quality checks.",
    )

    model_config = ConfigDict(extra="forbid")


class FieldExtractionResult(BaseModel):
    """Result of the structured-field extraction stage.

    Wraps the structured facts pulled from the document text. The worker
    inspects the extracted data to decide whether required business fields
    (notably the property address) are present.
    """

    extracted: ExtractedData = Field(
        description="Structured facts extracted from the document text.",
    )

    model_config = ConfigDict(extra="forbid")


class EnrichmentOutcome(StrEnum):
    """Terminal outcome of the hazard-enrichment stage.

    ``ENRICHED`` means a county FIPS was resolved and a hazard row was found,
    so the pipeline may proceed to summary generation. ``NEEDS_REVIEW`` means
    enrichment could not produce usable public hazard context (geocode failure
    or no hazard data for the resolved county); the orchestrator routes the
    submission to broker review rather than inventing data. This mirrors the
    missing-required-field gate and is a normal outcome, NOT an exception.
    """

    ENRICHED = "ENRICHED"
    NEEDS_REVIEW = "NEEDS_REVIEW"


class EnrichmentResult(BaseModel):
    """Result of the hazard-enrichment stage.

    Wraps public hazard data joined to the insured location by county FIPS,
    the resolved FIPS, and the public data-source provenance actually used.
    Carries a typed ``outcome`` so the orchestrator can route to NEEDS_REVIEW
    without the stage raising. When ``outcome`` is NEEDS_REVIEW, ``hazards`` is
    None and ``review_reason`` holds a broker-readable explanation.
    """

    outcome: EnrichmentOutcome = Field(
        description="Whether enrichment produced usable hazard context or needs broker review.",
    )
    county_fips: str | None = Field(
        default=None,
        description="5-digit county FIPS resolved for the insured location, or None if geocode failed.",
    )
    hazards: HazardData | None = Field(
        default=None,
        description="Public hazard data joined for the insured location. None when outcome is NEEDS_REVIEW.",
    )
    sources: list[DataSource] = Field(
        default_factory=list,
        description="Public data sources (FEMA NRI, NOAA Storm Events, Census geocoder) used to build this result.",
    )
    review_reason: str | None = Field(
        default=None,
        description="Broker-readable reason enrichment needs review. Set only when outcome is NEEDS_REVIEW.",
    )

    model_config = ConfigDict(extra="forbid")
