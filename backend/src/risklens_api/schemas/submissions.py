"""Pydantic request/response models matching the API contract."""

from __future__ import annotations

from datetime import datetime

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator

from risklens_api.core.constants import SubmissionStatus

# ---------------------------------------------------------------------------
# Requests -- use validation_alias to accept camelCase JSON input
# ---------------------------------------------------------------------------


class UploadUrlRequest(BaseModel):
    """Request body for creating a new submission upload intent.

    Initiates the upload flow by specifying the file metadata. The server
    validates content type and size, creates a submission record, and returns
    a presigned S3 URL for direct browser upload.
    """

    file_name: str = Field(
        validation_alias="fileName",
        description="Original filename of the document being uploaded.",
    )
    content_type: str = Field(
        validation_alias="contentType",
        description="MIME type of the file. Must be one of: application/pdf, image/png, image/jpeg, text/plain.",
    )
    file_size_bytes: int = Field(
        validation_alias="fileSizeBytes",
        gt=0,
        description="Size of the file in bytes. Must be positive and below the configured maximum.",
    )

    model_config = ConfigDict(populate_by_name=True)


class StartProcessingRequest(BaseModel):
    """Request body for initiating async processing of an uploaded submission.

    Sent after the client has completed the S3 upload. The object key confirms
    which uploaded artifact should be processed. The operation is idempotent —
    calling it on an already-queued submission is a no-op.
    """

    object_key: str = Field(
        validation_alias="objectKey",
        description="S3 object key of the uploaded file, as returned by the upload-url endpoint.",
    )

    model_config = ConfigDict(populate_by_name=True)


# ---------------------------------------------------------------------------
# Responses -- use serialization_alias for camelCase JSON output
# ---------------------------------------------------------------------------


class UploadUrlResponse(BaseModel):
    """Response from the upload-url endpoint containing the presigned URL and submission metadata.

    The client uses the uploadUrl to PUT the file directly to S3, then calls
    the start endpoint with the returned objectKey.
    """

    submission_id: str = Field(
        serialization_alias="submissionId",
        description="Unique sortable identifier for the created submission.",
    )
    upload_url: str = Field(
        serialization_alias="uploadUrl",
        description="Presigned S3 PUT URL for direct file upload. Expires after expiresInSeconds.",
    )
    object_key: str = Field(
        serialization_alias="objectKey",
        description="S3 object key where the file will be stored.",
    )
    expires_in_seconds: int = Field(
        serialization_alias="expiresInSeconds",
        description="Number of seconds until the presigned upload URL expires.",
    )
    max_file_size_bytes: int = Field(
        serialization_alias="maxFileSizeBytes",
        description="Maximum allowed file size in bytes for this upload.",
    )

    model_config = ConfigDict(serialize_by_alias=True)


class StartProcessingResponse(BaseModel):
    """Response confirming that processing has been queued for a submission.

    Returns the current status, which will be QUEUED on first call or the
    current advanced status if already past the UPLOADED state (idempotent).
    """

    submission_id: str = Field(
        serialization_alias="submissionId",
        description="Identifier of the submission that was started.",
    )
    status: SubmissionStatus = Field(
        description="Current status of the submission after the start operation.",
    )

    model_config = ConfigDict(serialize_by_alias=True)


class ProgressInfo(BaseModel):
    """Real-time progress details for an in-flight submission.

    Populated only while the submission is actively being processed.
    Null when the submission is in a terminal state (READY, FAILED).
    """

    current_step: str | None = Field(
        None,
        serialization_alias="currentStep",
        description="Human-readable label of the current processing step.",
    )
    percent: int | None = Field(
        None,
        description="Estimated completion percentage (0-100) of the overall pipeline.",
    )

    model_config = ConfigDict(serialize_by_alias=True)


class FileInfo(BaseModel):
    """Metadata about the originally uploaded file."""

    file_name: str = Field(
        serialization_alias="fileName",
        description="Original filename as provided during upload.",
    )
    content_type: str = Field(
        serialization_alias="contentType",
        description="MIME type of the uploaded file.",
    )

    model_config = ConfigDict(serialize_by_alias=True)


class SubmissionStatusResponse(BaseModel):
    """Full status response for a single submission, used for polling.

    Includes current processing state, timestamps, progress details,
    and file metadata. The frontend polls this endpoint every 2-5 seconds
    until the submission reaches a terminal state.
    """

    submission_id: str = Field(
        serialization_alias="submissionId",
        description="Unique identifier of the submission.",
    )
    status: SubmissionStatus = Field(
        description="Current processing status of the submission.",
    )
    created_at: datetime = Field(
        serialization_alias="createdAt",
        description="ISO 8601 UTC timestamp when the submission was created.",
    )
    updated_at: datetime = Field(
        serialization_alias="updatedAt",
        description="ISO 8601 UTC timestamp of the last status transition.",
    )
    progress: ProgressInfo | None = Field(
        None,
        description="Real-time progress info. Null for terminal states.",
    )
    file: FileInfo = Field(
        description="Metadata about the originally uploaded file.",
    )
    error: str | None = Field(
        None,
        description="Human-readable error message if the submission failed.",
    )

    model_config = ConfigDict(serialize_by_alias=True)


# ---------------------------------------------------------------------------
# Summary sub-models
# ---------------------------------------------------------------------------


class Address(BaseModel):
    """Structured address extracted from the submission document.

    Fields may be null if the OCR/extraction pipeline could not identify them.
    The county FIPS code is used to join public hazard datasets.
    """

    line1: str | None = Field(
        None, description="Street address line."
    )
    city: str | None = Field(
        None, description="City name."
    )
    state: str | None = Field(
        None, description="Two-letter US state abbreviation."
    )
    postal_code: str | None = Field(
        None,
        validation_alias=AliasChoices("postal_code", "postalCode"),
        serialization_alias="postalCode",
        description="ZIP or postal code.",
    )
    county_fips: str | None = Field(
        None,
        validation_alias=AliasChoices("county_fips", "countyFips"),
        serialization_alias="countyFips",
        description="5-digit county FIPS code used for hazard data lookups.",
    )

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)


class Limits(BaseModel):
    """Coverage limits requested in the submission, in USD."""

    building: int | None = Field(
        None, description="Building coverage limit in USD."
    )
    business_personal_property: int | None = Field(
        None,
        validation_alias=AliasChoices(
            "business_personal_property", "businessPersonalProperty"
        ),
        serialization_alias="businessPersonalProperty",
        description="Business personal property coverage limit in USD.",
    )

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)


class ExtractedData(BaseModel):
    """Structured facts extracted from the submission document by the GenAI pipeline.

    Fields are populated by Bedrock extraction. Missing or ambiguous fields
    are listed in missing_fields and may trigger NEEDS_REVIEW status.
    """

    insured_name: str | None = Field(
        None,
        validation_alias=AliasChoices("insured_name", "insuredName"),
        serialization_alias="insuredName",
        description="Name of the insured party or business.",
    )
    address: Address | None = Field(
        None, description="Structured address of the insured property."
    )
    industry: str | None = Field(
        None, description="Industry or occupancy classification."
    )
    requested_coverage: str | None = Field(
        None,
        validation_alias=AliasChoices("requested_coverage", "requestedCoverage"),
        serialization_alias="requestedCoverage",
        description="Type of insurance coverage requested (e.g. Commercial property).",
    )
    limits: Limits | None = Field(
        None, description="Coverage limits requested."
    )
    missing_fields: list[str] = Field(
        default_factory=list,
        validation_alias=AliasChoices("missing_fields", "missingFields"),
        serialization_alias="missingFields",
        description="List of field names that could not be extracted from the document.",
    )

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)


class StormEventCounts(BaseModel):
    """10-year storm event counts from NOAA Storm Events database for the county."""

    hail: int = Field(
        0, description="Number of hail events in the past 10 years."
    )
    strong_wind: int = Field(
        0,
        validation_alias=AliasChoices("strong_wind", "strongWind"),
        serialization_alias="strongWind",
        description="Number of strong wind events in the past 10 years.",
    )
    flash_flood: int = Field(
        0,
        validation_alias=AliasChoices("flash_flood", "flashFlood"),
        serialization_alias="flashFlood",
        description="Number of flash flood events in the past 10 years.",
    )

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)


class HazardData(BaseModel):
    """Public hazard and disaster data enrichment for the insured location.

    Sourced from FEMA National Risk Index, NOAA Storm Events, and
    FEMA disaster declarations. Used to inform the AI triage brief.
    """

    fema_risk_rating: str | None = Field(
        None,
        validation_alias=AliasChoices("fema_risk_rating", "femaRiskRating"),
        serialization_alias="femaRiskRating",
        description="FEMA National Risk Index overall risk rating for the county.",
    )
    top_hazards: list[str] = Field(
        default_factory=list,
        validation_alias=AliasChoices("top_hazards", "topHazards"),
        serialization_alias="topHazards",
        description="Top natural hazards identified for this location.",
    )
    recent_disaster_declarations: int = Field(
        0,
        validation_alias=AliasChoices(
            "recent_disaster_declarations", "recentDisasterDeclarations"
        ),
        serialization_alias="recentDisasterDeclarations",
        description="Number of FEMA disaster declarations in the county in recent years.",
    )
    storm_event_counts_10yr: StormEventCounts | None = Field(
        None,
        validation_alias=AliasChoices(
            "storm_event_counts_10yr", "stormEventCounts10Yr"
        ),
        serialization_alias="stormEventCounts10Yr",
        description="Breakdown of storm events by type over the past 10 years.",
    )

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)


class AIBrief(BaseModel):
    """AI-generated underwriting triage brief produced by Amazon Bedrock.

    This is a broker-reviewable draft, not a binding decision. All claims
    are grounded in extracted facts and public hazard data.
    """

    executive_summary: str | None = Field(
        None,
        validation_alias=AliasChoices("executive_summary", "executiveSummary"),
        serialization_alias="executiveSummary",
        description="One-paragraph overview of the submission's risk profile and triage recommendation.",
    )
    risk_flags: list[str] = Field(
        default_factory=list,
        validation_alias=AliasChoices("risk_flags", "riskFlags"),
        serialization_alias="riskFlags",
        description="Key risk concerns identified from document and hazard data.",
    )
    questions_for_broker: list[str] = Field(
        default_factory=list,
        validation_alias=AliasChoices("questions_for_broker", "questionsForBroker"),
        serialization_alias="questionsForBroker",
        description="Suggested follow-up questions for the broker to clarify.",
    )
    confidence: str | None = Field(
        None,
        description="Model confidence level: high, medium, or low.",
    )

    @field_validator("confidence", mode="before")
    @classmethod
    def _coerce_confidence(cls, value: object) -> str | None:
        """Normalize confidence into a categorical bucket.

        The model sometimes emits a numeric probability (e.g. 0.38) instead of
        the requested categorical value. Map numerics in [0, 1] to high/medium/
        low buckets and pass through recognized strings.
        """
        if value is None:
            return None
        if isinstance(value, bool):
            return "high" if value else "low"
        if isinstance(value, (int, float)):
            score = float(value)
            if score >= 0.66:
                return "high"
            if score >= 0.33:
                return "medium"
            return "low"
        return str(value)

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)


class DataSource(BaseModel):
    """Reference to a public data source used during enrichment."""

    name: str = Field(description="Display name of the data source.")
    url: str = Field(description="URL where the data source can be accessed or verified.")


class SummaryResponse(BaseModel):
    """Complete triage summary response including extracted data, hazard enrichment, and AI brief.

    Only available when the submission status is READY or NEEDS_REVIEW.
    Combines document extraction, public data enrichment, and the
    Bedrock-generated underwriting triage brief.
    """

    submission_id: str = Field(
        serialization_alias="submissionId",
        description="Identifier of the submission.",
    )
    status: SubmissionStatus = Field(
        description="Current status (READY or NEEDS_REVIEW when summary is available).",
    )
    extracted: ExtractedData | None = Field(
        None, description="Structured facts extracted from the submission document."
    )
    hazards: HazardData | None = Field(
        None, description="Public hazard data enrichment for the insured location."
    )
    ai_brief: AIBrief | None = Field(
        default=None,
        serialization_alias="aiBrief",
        description="AI-generated underwriting triage brief.",
    )
    sources: list[DataSource] = Field(
        default_factory=list,
        description="Public data sources referenced during enrichment.",
    )

    model_config = ConfigDict(serialize_by_alias=True)


# ---------------------------------------------------------------------------
# List endpoint
# ---------------------------------------------------------------------------


class SubmissionListItem(BaseModel):
    """Summary item for a single submission in the list view."""

    submission_id: str = Field(
        serialization_alias="submissionId",
        description="Unique identifier of the submission.",
    )
    status: SubmissionStatus = Field(
        description="Current processing status.",
    )
    created_at: datetime = Field(
        serialization_alias="createdAt",
        description="ISO 8601 UTC timestamp when the submission was created.",
    )
    file_name: str = Field(
        serialization_alias="fileName",
        description="Original filename of the uploaded document.",
    )

    model_config = ConfigDict(serialize_by_alias=True)


class SubmissionListResponse(BaseModel):
    """Paginated list of submission summaries.

    Use nextToken to retrieve subsequent pages. Items are ordered by
    creation time descending (most recent first).
    """

    items: list[SubmissionListItem] = Field(
        description="Submission summaries for the current page.",
    )
    next_token: str | None = Field(
        None,
        serialization_alias="nextToken",
        description="Opaque cursor token for fetching the next page. Null if no more results.",
    )

    model_config = ConfigDict(serialize_by_alias=True)
