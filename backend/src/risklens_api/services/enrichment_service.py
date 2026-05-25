"""Public-data hazard enrichment service and its resolution collaborators.

This module hosts the real :class:`EnrichmentService` implementation behind the
worker Protocol, plus the two narrow seams it depends on:

- a :class:`GeocodeService` that resolves an address to a 5-digit county FIPS,
- a :class:`HazardRepository` that reads county-keyed hazard summaries.

For the MVP slice both seams are backed by tiny SYNTHETIC in-repo fixtures
(``hazard_fixtures``); production adapters that call the US Census Geocoder and
read the Terraform-managed S3/Dynamo hazard cache are left as clearly-marked
TODO seams. No HTTP or AWS calls are made here.

Enrichment normalizes on county FIPS. If geocode cannot resolve a FIPS, or no
hazard row exists for the resolved FIPS, the service returns a NEEDS_REVIEW
outcome with a broker-readable reason rather than raising or inventing data.
"""

from __future__ import annotations

from risklens_api.core.logging import get_logger
from risklens_api.schemas.processing import EnrichmentOutcome, EnrichmentResult
from risklens_api.schemas.submissions import Address, ExtractedData, HazardData
from risklens_api.services.hazard_fixtures import (
    CENSUS_GEOCODER_SOURCE,
    HAZARD_SUMMARY_SOURCES,
    SAMPLE_CITY_STATE_FIPS,
    SAMPLE_COUNTY_HAZARDS,
    SAMPLE_POSTAL_FIPS,
)
from risklens_api.worker.protocols import GeocodeService, HazardRepository

_COMPONENT = "enrichment"

GEOCODE_FAILED_REASON = (
    "Insured location could not be resolved to a US county. "
    "Broker review required to confirm the property address."
)
HAZARD_MISSING_REASON_TEMPLATE = (
    "No public hazard data is available for county FIPS {fips}. "
    "Broker review required before relying on hazard context."
)


class FixtureGeocodeService:
    """Fixture-backed county-FIPS resolver for local dev and tests.

    Resolution order, all from tiny synthetic fixtures:

    1. An ``Address.county_fips`` already present and known to the fixtures.
    2. A ``city`` + ``state`` match.
    3. A ``postal_code`` match.

    Returns None (never raises) when nothing matches.

    TODO(prod): add ``CensusGeocodeService`` here that calls the US Census
    Geocoder one-line/address HTTP API and maps the response geographies to a
    county FIPS. Keep the same ``resolve_county_fips`` signature so the
    enrichment stage is unchanged.
    """

    def resolve_county_fips(self, address: Address) -> str | None:
        if address is None:  # type: ignore[redundant-expr]
            return None

        if address.county_fips and address.county_fips in SAMPLE_COUNTY_HAZARDS:
            return address.county_fips

        if address.city and address.state:
            key = f"{address.city.strip().upper()}|{address.state.strip().upper()}"
            fips = SAMPLE_CITY_STATE_FIPS.get(key)
            if fips:
                return fips

        if address.postal_code:
            fips = SAMPLE_POSTAL_FIPS.get(address.postal_code.strip())
            if fips:
                return fips

        return None


class FixtureHazardRepository:
    """Fixture-backed county hazard cache for local dev and tests.

    Reads from the synthetic ``SAMPLE_COUNTY_HAZARDS`` map. Returns None when
    no row exists for the requested FIPS.

    TODO(prod): add an ``S3DynamoHazardRepository`` that reads the normalized
    county records from the Terraform ``mrisk`` hazard cache. Keep the same
    ``get_by_fips`` signature.
    """

    def get_by_fips(self, county_fips: str) -> HazardData | None:
        return SAMPLE_COUNTY_HAZARDS.get(county_fips)


class HazardEnrichmentService:
    """Real hazard-enrichment stage backed by injectable resolution seams.

    Collaborators are injected so the same service runs against fixtures in
    tests and against Census/S3/Dynamo adapters in production. Defaults wire the
    fixture-backed implementations so the service is directly usable in tests.
    """

    def __init__(
        self,
        geocoder: GeocodeService | None = None,
        hazards: HazardRepository | None = None,
    ) -> None:
        self._geocoder = geocoder or FixtureGeocodeService()
        self._hazards = hazards or FixtureHazardRepository()
        self._logger = get_logger()

    def enrich(
        self, submission_id: str, extracted: ExtractedData
    ) -> EnrichmentResult:
        address = extracted.address

        # --- Resolve county FIPS (single resolution path) ---
        county_fips = (
            self._geocoder.resolve_county_fips(address)
            if address is not None
            else None
        )
        if county_fips is None:
            self._log_review(submission_id, "geocode_unresolved", county_fips=None)
            return EnrichmentResult(
                outcome=EnrichmentOutcome.NEEDS_REVIEW,
                county_fips=None,
                hazards=None,
                sources=[CENSUS_GEOCODER_SOURCE],
                review_reason=GEOCODE_FAILED_REASON,
            )

        # --- Read county hazard summary from the cache ---
        hazard_data = self._hazards.get_by_fips(county_fips)
        if hazard_data is None:
            self._log_review(
                submission_id, "hazard_row_missing", county_fips=county_fips
            )
            return EnrichmentResult(
                outcome=EnrichmentOutcome.NEEDS_REVIEW,
                county_fips=county_fips,
                hazards=None,
                sources=[CENSUS_GEOCODER_SOURCE],
                review_reason=HAZARD_MISSING_REASON_TEMPLATE.format(fips=county_fips),
            )

        # --- Success: hazard data with full provenance ---
        return EnrichmentResult(
            outcome=EnrichmentOutcome.ENRICHED,
            county_fips=county_fips,
            hazards=hazard_data,
            sources=[CENSUS_GEOCODER_SOURCE, *HAZARD_SUMMARY_SOURCES],
            review_reason=None,
        )

    def _log_review(
        self, submission_id: str, cause: str, county_fips: str | None
    ) -> None:
        """Emit one structured log line for a review-needed enrichment outcome.

        Logs only non-PII identifiers and the resolved FIPS (no raw address,
        document text, or dataset rows).
        """
        self._logger.info(
            "Enrichment needs broker review",
            extra={
                "component": _COMPONENT,
                "submission_id": submission_id,
                "status": EnrichmentOutcome.NEEDS_REVIEW,
                "cause": cause,
                "county_fips": county_fips,
            },
        )
